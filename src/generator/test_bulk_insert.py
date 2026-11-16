
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


def main():
    # 1. Generate five valid transfers
    accounts_by_currency = get_accounts_by_currency()
    transfers = generate_transfers(accounts_by_currency, 5)

    print(f"Generated: {len(transfers)}")

    # 2. Read staging table SQL
    staging_sql = Path(
        "sql/postgres/006_transfer_staging.sql"
    ).read_text()

    # 3. Create a unique identifier for this batch
    batch_id = uuid4()

    # 4. Open one PostgreSQL transaction
    with psycopg.connect(
        host="localhost",
        port=5433,
        dbname="bankflow",
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    ) as conn:

        # Create temporary staging table
        with conn.cursor() as cur:
            cur.execute(staging_sql)

        # 5. Copy generated records into staging
        copied = copy_to_staging(conn, transfers)
        print(f"Copied to staging: {copied}")

        # 6. Insert into permanent transfers table
        inserted = insert_staged_transfers(conn, batch_id)
        print(f"First insertion: {inserted}")

        # 7. Retry with the same batch ID
        inserted_again = insert_staged_transfers(conn, batch_id)
        print(f"Second insertion: {inserted_again}")

        # 8. Verify the permanent records
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    transfer_id,
                    source_row_num,
                    amount,
                    currency
                FROM transfers
                WHERE source_batch_id = %s
                ORDER BY source_row_num
            """, (batch_id,))

            rows = cur.fetchall()

        print(f"Verified in PostgreSQL: {len(rows)}")

        for row in rows:
            print(row)

        # 9. Validate results
        assert copied == 5
        assert inserted == 5
        assert inserted_again == 0
        assert len(rows) == 5
        ledger_inserted = insert_ledger_entries(conn, batch_id)
        print(f"Ledger entries inserted: {ledger_inserted}")
        assert ledger_inserted == 10
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    t.transfer_id,
                    COUNT(le.entry_id) AS entry_count,
                    SUM(le.amount) FILTER (
                        WHERE le.entry_type = 'DEBIT'
                    ) AS total_debit,
                    SUM(le.amount) FILTER (
                        WHERE le.entry_type = 'CREDIT'
                    ) AS total_credit
                FROM transfers t
                LEFT JOIN ledger_entries le
                    ON t.transfer_id = le.transfer_id
                WHERE t.source_batch_id = %s
                GROUP BY t.transfer_id
                ORDER BY t.transfer_id;
            """, (batch_id,))

            ledger_rows = cur.fetchall()

        assert len(ledger_rows) == 5

        for transfer_id, entry_count, total_debit, total_credit in ledger_rows:
            assert entry_count == 2, f"Transfer {transfer_id}: {entry_count} entries"
            assert total_debit is not None
            assert total_credit is not None
            assert total_debit == total_credit, (
                f"Transfer {transfer_id} is unbalanced!"
            )

        print(f"Balanced transfers: {len(ledger_rows)} / 5")

        # 10. Roll back everything
        conn.rollback()
        print("Transaction rolled back successfully")


if __name__ == "__main__":
    main()
