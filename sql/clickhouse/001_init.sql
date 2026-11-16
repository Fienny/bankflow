create table if not exists raw_transfers (
    transfer_id Int64,
    from_account_id Int64,
    to_account_id Int64,
    amount Decimal(18, 2),
    currency FixedString(3),
    status String,
    created_at Datetime64(6, 'UTC')
)
Engine = MergeTree()
ORDER BY (created_at, transfer_id);