import os
from pathlib import Path
from uuid import uuid4

import psycopg
from dotenv import load_dotenv

from src.generator.generate_transfers import (
    get_accounts_by_currency,
    generate_transfers,
)

from src.generator.load_generated_transfers import (
    copy_to_staging,
    insert_staged_transfers,
    insert_ledger_entries,
)

load_dotenv()

BATCH_SIZE = 10_000

def main():
    transfers = generate_transfers(get_accounts_by_currency(), BATCH_SIZE)
    with psycopg.connect(
        host="localhost",
        port=5433,
        dbname="bankflow",
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    ) as conn:
        # Create a unique batch ID for this run
        batch_id = uuid4()

        # Create the staging table
        staging_sql = Path("sql/postgres/006_transfer_staging.sql").read_text()
        with conn.cursor() as cur:
            cur.execute(staging_sql)

        # Copy generated transfers to the staging table
        copied = copy_to_staging(conn, transfers)
        print(f"Copied {copied} transfers to staging.")

        # Insert staged transfers into the main transfers table
        inserted = insert_staged_transfers(conn, batch_id)
        print(f"Inserted {inserted} transfers into the main table.")

        # Insert ledger entries for the inserted transfers
        ledger_inserted = insert_ledger_entries(conn, batch_id)
        print(f"Inserted {ledger_inserted} ledger entries.")

        # Validate the batch
        with conn.cursor() as cur:
            cur.execute("""
                SELECT COUNT(*)
                FROM (
                    SELECT
                        t.transfer_id
                    FROM transfers t
                    LEFT JOIN ledger_entries l
                        ON t.transfer_id = l.transfer_id
                    WHERE t.source_batch_id = %s
                    GROUP BY
                        t.transfer_id,
                        t.from_account_id,
                        t.to_account_id,
                        t.amount
                    HAVING
                        COUNT(l.entry_id) <> 2
                        OR COALESCE(SUM(l.amount) FILTER (
                            WHERE l.entry_type = 'DEBIT'
                        ), 0) <> t.amount
                        OR COALESCE(SUM(l.amount) FILTER (
                            WHERE l.entry_type = 'CREDIT'
                        ), 0) <> t.amount
                        OR MAX(l.account_id) FILTER (
                            WHERE l.entry_type = 'DEBIT'
                        ) IS DISTINCT FROM t.from_account_id
                        OR MAX(l.account_id) FILTER (
                            WHERE l.entry_type = 'CREDIT'
                        ) IS DISTINCT FROM t.to_account_id
                ) AS invalid_transfers;
            """, (batch_id,))

            invalid_count = cur.fetchone()[0]
        
        print(f"Batch {batch_id} committed successfully!")

        assert copied == BATCH_SIZE
        assert inserted == BATCH_SIZE
        assert ledger_inserted == BATCH_SIZE * 2
        assert invalid_count == 0, (
            f"Found {invalid_count} invalid transfers!"
        )

        print(f"Validated transfers: {BATCH_SIZE} / {BATCH_SIZE}")

if __name__ == "__main__":
    main()