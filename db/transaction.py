"""Helpers cho transaction psycopg2."""

from contextlib import contextmanager

from db.connections import get_connection


@contextmanager
def transaction(site_code):
    """Mo transaction va tu dong commit/rollback."""
    conn = get_connection(site_code)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
