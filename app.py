"""Entry point for the distributed course registration project."""

from db.connections import DB_CONFIGS, SITE_CODES


def main():
    print("BTL CSDLPT - Dang ky hoc phan")
    print("Configured distributed PostgreSQL sites:")
    for site_code in SITE_CODES:
        config = DB_CONFIGS[site_code]
        print(
            f"- {site_code}: {config['database']} "
            f"at {config['host']}:{config['port']}"
        )


if __name__ == "__main__":
    main()
