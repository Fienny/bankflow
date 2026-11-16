import os
import psycopg
from dotenv import load_dotenv
from decimal import Decimal
import random

load_dotenv()

def get_accounts_by_currency() -> dict[str, list[int]]:
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
                currency,
                array_agg(account_id ORDER BY account_id) AS account_ids
            FROM accounts
            GROUP BY currency
            ORDER BY currency;
            """)
            result = cur.fetchall()
    return {row[0]: row[1] for row in result}

# Generate transfers
# Each should contain:
# (
#     from_account_id,
#     to_account_id,
#     amount,
#     currency,
#     status
# )
def generate_transfers(
    accounts_by_currency: dict[str, list[int]],
    count: int
) -> list[tuple]:
    random.seed(42)  # Seed for reproducibility
    transfers = []
    eligible_currencies = [
        currency
        for currency, account_ids in accounts_by_currency.items()
        if len(account_ids) >= 2
    ]

    if count > 0 and not eligible_currencies:
        raise ValueError("No currencies have at least two accounts")

    for _ in range(count):
        currency = random.choice(eligible_currencies)
        account_ids = accounts_by_currency[currency]
        from_account_id, to_account_id = random.sample(account_ids, 2)
        amount = Decimal(random.randint(100, 100000)) / Decimal("100")
        status = "COMPLETED"
        transfers.append((from_account_id, to_account_id, amount, currency, status))
    assert len(transfers) == count
    assert all(t[0] != t[1] for t in transfers)
    assert all(t[2] > 0 for t in transfers)
    assert all(t[4] == "COMPLETED" for t in transfers)
    assert all(
        # sender belongs to the currency group
        # AND receiver belongs to the same group
        t[0] in accounts_by_currency[t[3]] and t[1] in accounts_by_currency[t[3]]
        for t in transfers
    )

    return transfers


if __name__ == "__main__":
    accounts_by_currency = get_accounts_by_currency()

    transfers = generate_transfers(accounts_by_currency, 10_000)
    print(f"Generated {len(transfers):,} transfers")
    print("Sample:", transfers[:5])
