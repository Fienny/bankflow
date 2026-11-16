ALTER TABLE transfers
    ADD COLUMN source_batch_id UUID,
    ADD COLUMN source_row_num BIGINT,
    ADD CONSTRAINT uq_transfer_source
        UNIQUE (source_batch_id, source_row_num);