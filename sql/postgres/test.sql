SELECT
    c.full_name,
    a.account_id,
    a.currency,
    a.account_type
FROM accounts a
JOIN customers c
    ON a.customer_id = c.customer_id
ORDER BY a.account_id;
