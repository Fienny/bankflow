import os
import psycopg
from dotenv import load_dotenv
import clickhouse_connect


# 1. Load environment variables
load_dotenv()

# 2. Get credentials
user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")

# 3. Connect to PostgreSQL
with psycopg.connect(
    host="localhost",
    port=5433,
    dbname="bankflow",
    user=user,
    password=password
) as conn:
    # 4. Create a cursor
    with conn.cursor() as cur:
        cur.execute("select count(*) from transfers")

        count = cur.fetchone()[0]
        print(f"Total number of transfers: {count}")

# ClickHouse connection
ch_client = clickhouse_connect.get_client(
    host="localhost",
    port=8123,
    username=os.getenv("CLICKHOUSE_USER"),
    password=os.getenv("CLICKHOUSE_PASSWORD"),
    database="bankflow"
)

result = ch_client.query("SELECT version()")

print(f"ClickHouse version: {result.result_rows[0][0]}")

ch_client.close()