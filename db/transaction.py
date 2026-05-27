"""Tầng truy cập dữ liệu cho nghiệp vụ transaction, thực hiện đọc/ghi PostgreSQL theo site."""

from contextlib import contextmanager

from db.connections import get_connection


# Bao một khối thao tác database trong giao dịch, tự commit khi thành công và rollback khi lỗi.
@contextmanager
def transaction(site_code):
    """Bao một khối thao tác database trong giao dịch, tự commit khi thành công và rollback khi lỗi."""
    conn = get_connection(site_code)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
