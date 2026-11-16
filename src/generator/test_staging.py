from pathlib import Path
import psycopg
import os
from dotenv import load_dotenv

from src.generator.generate_transfers import (
    get_accounts_by_currency,
    generate_transfers
)

from src.generator.load_generated_transfers import copy_to_staging

load_dotenv()

sql = Path("sql/postgres/006_transfer_staging.sql").read_text()

with psycopg.connect(
    host="localhost",
    port=5433,
    dbname="bankflow",
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD")
) as conn:
    with conn.cursor() as cur:
        cur.execute(sql)

    transfers = generate_transfers(get_accounts_by_currency(), 100)
    copied = copy_to_staging(conn, transfers)

    # Query staging row count
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM staging_transfers")
        row_count = cur.fetchone()[0]
        print(f"Copied {copied} transfers to staging. Staging row count: {row_count}")
    assert copied == row_count == 100
    # Roll back
    conn.rollback()