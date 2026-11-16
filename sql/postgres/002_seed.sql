-- insert two customers
INSERT INTO customers (full_name)
VALUES ('Alice Smith'), ('Bob Johnson')
RETURNING customer_id;

-- insert accounts for our users
INSERT INTO accounts (customer_id, currency, account_type)
VALUES
    (1, 'USD', 'savings'),
    (1, 'UZS', 'current'),
    (2, 'UZS', 'current')
returning account_id;

-- test
-- select
--     c.full_name,
--     a.account_id,
--     a.currency,
--     a.account_type
-- from customers c
-- join accounts a
--     on c.customer_id = a.customer_id;