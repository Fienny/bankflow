from faker import Faker
import psycopg
from dotenv import load_dotenv
import os

load_dotenv()

def generate_customers(count: int) -> list[tuple]:
    Faker.seed(42)  # Seed for reproducibility
    fake = Faker()

    return [(fake.name(),) for _ in range(count)]

def insert_customers(customers: list[tuple]) -> int:
    with psycopg.connect(
        host="localhost",
        port=5433,
        dbname="bankflow",
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    ) as conn:
        with conn.cursor() as cur:
            cur.executemany(
                "INSERT INTO customers (full_name) VALUES (%s)",
                customers
            )
            conn.commit()
            return len(customers)


if __name__ == "__main__":
    num_customers = 100  # Number of customers to generate
    customers = generate_customers(num_customers)
    print(f"Generated {len(customers)} customers:")
    print(customers)
    inserted_count = insert_customers(customers)
    print(f"Inserted {inserted_count} customers into the database.")