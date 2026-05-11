"""Helpers for running queries across all distributed sites."""

from db.connections import SITE_CODES, get_connection


def fetch_all_sites(sql, params=None):
    """Run a SELECT query on every site and return rows grouped by site code."""
    results = {}
    for site_code in SITE_CODES:
        with get_connection(site_code) as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                results[site_code] = cursor.fetchall()
    return results


def execute_all_sites(sql, params=None):
    """Run a write query on every site and commit each site independently."""
    for site_code in SITE_CODES:
        with get_connection(site_code) as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
            conn.commit()
