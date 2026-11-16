ALTER TABLE ledger_entries
    ADD CONSTRAINT uq_ledger_transfer_type
    UNIQUE (transfer_id, entry_type);