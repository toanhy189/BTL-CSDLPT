"""Tầng truy cập dữ liệu cho nghiệp vụ kết nối, thực hiện đọc/ghi PostgreSQL theo site."""

import psycopg2


DB_CONFIGS = {
    "HL": {
        "host": "localhost",
        "port": 5440,
        "database": "site_hoalac",
        "user": "postgres",
        "password": "toantk178@",
    },
    "NT": {
        "host": "localhost",
        "port": 5441,
        "database": "site_ngoctruc",
        "user": "postgres",
        "password": "toantk178@",
    },
    "HD": {
        "host": "localhost",
        "port": 5442,
        "database": "site_hadong",
        "user": "postgres",
        "password": "toantk178@",
    },
    "CG": {
        "host": "localhost",
        "port": 5443,
        "database": "site_caugiay",
        "user": "postgres",
        "password": "toantk178@",
    },
    "HCM": {
        "host": "localhost",
        "port": 5444,
        "database": "site_hcm",
        "user": "postgres",
        "password": "toantk178@",
    },
}

SITE_CODES = ["HL", "NT", "HD", "CG", "HCM"]
SITE_NAMES = {
    "HL": "Hòa Lạc",
    "NT": "Ngọc Trục",
    "HD": "Hà Đông",
    "CG": "Cầu Giấy",
    "HCM": "TP.HCM",
}


# Mở kết nối PostgreSQL đến đúng site/cơ sở theo mã được truyền vào.
def get_connection(site_code):
    config = DB_CONFIGS[site_code]
    return psycopg2.connect(**config)


# Lấy dữ liệu all kết nối từ nguồn phù hợp để trả về cho tầng gọi phía trên.
def get_all_connections():
    return {site_code: get_connection(site_code) for site_code in SITE_CODES}


# Thử kết nối một site và trả trạng thái để dashboard biết site online hay lỗi.
def check_site_connection(site_code):
    try:
        conn = get_connection(site_code)
        conn.close()
        return True, "Kết nối thành công"
    except Exception as exc:
        return False, str(exc)
