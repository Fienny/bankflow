
import psycopg


def copy_to_staging(conn, transfers: list[tuple]) -> int:
    with conn.cursor() as cur:
        with cur.copy("""
            COPY staging_transfers (
                from_account_id,
                to_account_id,
                amount,
                currency,
                status
            ) FROM STDIN
        """) as copy:
            for transfer in transfers:
                copy.write_row(transfer)

    return len(transfers)


def insert_staged_transfers(conn, batch_id) -> int:
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO transfers (
                from_account_id,
                to_account_id,
                amount,
                currency,
                status,
                source_batch_id,
                source_row_num
            )
            SELECT
                from_account_id,
                to_account_id,
                amount,
                currency,
                status,
                %s,
                row_num
            FROM staging_transfers
            WHERE TRUE
            ON CONFLICT (source_batch_id, source_row_num)
            DO NOTHING
        """, (batch_id,))

        return cur.rowcount
