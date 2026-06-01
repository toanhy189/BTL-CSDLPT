"""Tầng truy cập dữ liệu cho nghiệp vụ kết nối, thực hiện đọc/ghi PostgreSQL theo site."""

import psycopg2

from backend.core.config import DB_CONFIGS


# Mở kết nối PostgreSQL đến đúng site/cơ sở theo mã được truyền vào.
def get_connection(site_code):
    config = DB_CONFIGS[site_code]
    return psycopg2.connect(**config)


# Thử kết nối một site và trả trạng thái để dashboard biết site online hay lỗi.
def check_site_connection(site_code):
    try:
        conn = get_connection(site_code)
        conn.close()
        return True, "Kết nối thành công"
    except Exception as exc:
        return False, str(exc)
