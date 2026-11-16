import os
import clickhouse_connect
import psycopg
from dotenv import load_dotenv

load_dotenv()

def extract_transfers(last_loaded_id):
    with psycopg.connect(
        host="localhost",
        port=5433,
        dbname="bankflow",
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    ) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    transfer_id,
                    from_account_id,
                    to_account_id,
                    amount,
                    currency,
                    status,
                    created_at
                FROM transfers
                WHERE transfer_id > %s
                ORDER BY transfer_id
            """, (last_loaded_id,))

            rows = cur.fetchall()

    return rows

def load_transfers(transfers):
    client = clickhouse_connect.get_client(
        host="localhost",
        port=8123,
        username=os.getenv("CLICKHOUSE_USER"),
        password=os.getenv("CLICKHOUSE_PASSWORD"),
        database="bankflow"
    )
    try:
        client.insert(
            table="raw_transfers",
            data=transfers, 
            column_names=[
                "transfer_id",
                "from_account_id",
                "to_account_id",
                "amount",
                "currency",
                "status",
                "created_at"
            ]
        )
    finally:
        client.close()

def get_last_loaded_id():
    client = clickhouse_connect.get_client(
        host="localhost",
        port=8123,
        username=os.getenv("CLICKHOUSE_USER"),
        password=os.getenv("CLICKHOUSE_PASSWORD"),
        database="bankflow"
    )
    try:
        result = client.query("SELECT coalesce(MAX(transfer_id), 0) FROM raw_transfers;")
        last_loaded_id = result.result_rows[0][0]

        return last_loaded_id
    finally:
        client.close()



if __name__ == "__main__":
    last_loaded_id = get_last_loaded_id()

    transfers = extract_transfers(last_loaded_id)

    if not transfers:
        print("No new transfers to load.")
    else:
        print(f"Extracted {len(transfers)} transfers")
        for transfer in transfers:
            print(transfer)
        load_transfers(transfers)
        print(f"Loaded {len(transfers)} transfers into ClickHouse")

