"""Database connection helpers for the five distributed PostgreSQL sites."""

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


def get_connection(site_code):
    """Open a psycopg2 connection to one distributed site."""
    config = DB_CONFIGS[site_code]
    return psycopg2.connect(**config)


def get_all_connections():
    """Open connections to all configured distributed sites."""
    return {site_code: get_connection(site_code) for site_code in SITE_CODES}
