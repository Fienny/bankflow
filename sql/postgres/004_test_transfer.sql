
\set ON_ERROR_STOP on

BEGIN;

-- 1. Create a transfer: Alice -> Bob
INSERT INTO transfers (
    from_account_id,
    to_account_id,
    amount,
    currency
)
VALUES (
    2,
    3,
    200000.00,
    'UZS'
)
RETURNING transfer_id \gset

-- 2. Record the debit from Alice
INSERT INTO ledger_entries (
    transfer_id,
    account_id,
    amount,
    entry_type
)
VALUES (
    :transfer_id,
    2,
    200000.00,
    'DEBIT'
);

-- 3. Record the credit to Bob
INSERT INTO ledger_entries (
    transfer_id,
    account_id,
    amount,
    entry_type
)
VALUES (
    :transfer_id,
    3,
    200000.00,
    'CREDIT'
);

-- 4. Complete the transfer
UPDATE transfers
SET status = 'COMPLETED'
WHERE transfer_id = :transfer_id
  AND status = 'PENDING';

COMMIT;
