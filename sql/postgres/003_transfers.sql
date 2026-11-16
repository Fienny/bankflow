-- transfers
create table if not exists transfers (
    transfer_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    from_account_id BIGINT not null references accounts(account_id),
    to_account_id BIGINT not null references accounts(account_id)
        check (from_account_id <> to_account_id),
    amount numeric(18, 2) not null
        check (amount > 0),
    currency char(3) not null,
    status varchar(20) not null default 'PENDING'
        check (status in ('PENDING', 'COMPLETED', 'FAILED')),
    created_at TIMESTAMPTZ not null default now()
);

-- ledger_entries
create table if not exists ledger_entries (
    entry_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    transfer_id BIGINT not null references transfers(transfer_id),
    account_id BIGINT not null references accounts(account_id),
    amount numeric(18, 2) not null
        check (amount > 0),
    entry_type varchar(20) not null
        check (entry_type in ('DEBIT', 'CREDIT')),
    posted_at TIMESTAMPTZ not null default now()
);