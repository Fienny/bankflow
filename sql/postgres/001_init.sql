-- customers table
CREATE TABLE IF NOT EXISTS customers (
    customer_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- accounts table
CREATE TABLE IF NOT EXISTS accounts (
    account_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id BIGINT NOT NULL REFERENCES customers(customer_id),
    currency CHAR(3) NOT NULL,
    account_type VARCHAR(20) NOT NULL,
    opened_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

