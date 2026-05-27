"""Module phục vụ nghiệp vụ config trong hệ thống đăng ký học phần phân tán."""

import os


SITE_CODES = ["HL", "NT", "HD", "CG", "HCM"]

SITE_NAMES = {
    "HL": "Hòa Lạc",
    "NT": "Ngọc Trục",
    "HD": "Hà Đông",
    "CG": "Cầu Giấy",
    "HCM": "TP.HCM",
}

DB_PASSWORD = os.getenv("DB_PASSWORD", os.getenv("POSTGRES_PASSWORD", "toantk178@"))

DB_CONFIGS = {
    "HL": {
        "host": "localhost",
        "port": 5440,
        "database": "site_hoalac",
        "user": "postgres",
        "password": DB_PASSWORD,
    },
    "NT": {
        "host": "localhost",
        "port": 5441,
        "database": "site_ngoctruc",
        "user": "postgres",
        "password": DB_PASSWORD,
    },
    "HD": {
        "host": "localhost",
        "port": 5442,
        "database": "site_hadong",
        "user": "postgres",
        "password": DB_PASSWORD,
    },
    "CG": {
        "host": "localhost",
        "port": 5443,
        "database": "site_caugiay",
        "user": "postgres",
        "password": DB_PASSWORD,
    },
    "HCM": {
        "host": "localhost",
        "port": 5444,
        "database": "site_hcm",
        "user": "postgres",
        "password": DB_PASSWORD,
    },
}

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-this-secret-for-production")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "240"))

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
