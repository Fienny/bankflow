from faker import Faker
import psycopg
from dotenv import load_dotenv
import os
import random
load_dotenv()

def get_customer_ids() -> list[int]:
    with psycopg.connect(
        host="localhost",
        port=5433,
        dbname="bankflow",
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    ) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT customer_id FROM customers")
            return [row[0] for row in cur.fetchall()]

def generate_accounts(customer_ids: list[int], count: int) -> list[tuple]:
    random.seed(42)  # Seed for reproducibility
    accounts = []

    for _ in range(count):
        customer_id = random.choice(customer_ids)
        currency = random.choice(["USD", "EUR", "UZS"])
        account_type = random.choice(["current", "savings"])
        accounts.append((customer_id, currency, account_type))

    return accounts

def insert_accounts(accounts: list[tuple]) -> int:
    with psycopg.connect(
        host="localhost",
        port=5433,
        dbname="bankflow",
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    ) as conn:
        with conn.cursor() as cur:
            cur.executemany(
                "INSERT INTO accounts (customer_id, currency, account_type) VALUES (%s, %s, %s)",
                accounts
            )
            conn.commit()
            return len(accounts)

if __name__ == "__main__":
    print("Generating accounts...")
    customer_ids = get_customer_ids()
    num_accounts = 150  # Number of accounts to generate
    accounts = generate_accounts(customer_ids, num_accounts)
    print(f"Generated {len(accounts)} accounts:")
    print("Sample accounts:", accounts[:10])
    print("Unique customers:", len(set(a[0] for a in accounts)))
    inserted_count = insert_accounts(accounts)
    print(f"Inserted {inserted_count} accounts into the database.")