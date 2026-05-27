"""Module phục vụ nghiệp vụ seed data trong hệ thống đăng ký học phần phân tán."""

import random
import sys

from faker import Faker
from psycopg2.extras import execute_values

from db.connections import SITE_CODES, get_connection


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

fake = Faker("vi_VN")

# 1. Du lieu nhan ban tren ca 5 site.
CO_SO_DATA = [
    ("HL", "Co so Hoa Lac", "Khu CNC Hoa Lac, Thach That, Ha Noi"),
    ("NT", "Co so Ngoc Truc", "Ngoc Truc, Nam Tu Liem, Ha Noi"),
    ("HD", "Co so Ha Dong", "Ha Dong, Ha Noi"),
    ("CG", "Co so Cau Giay", "Cau Giay, Ha Noi"),
    ("HCM", "Co so TP.HCM", "TP.HCM"),
]

KHOA_DATA = [
    ("CNTT", "Khoa Cong nghe thong tin"),
    ("ATTT", "Khoa An toan thong tin"),
    ("DTVT", "Khoa Dien tu vien thong"),
    ("HTTT", "Khoa He thong thong tin"),
    ("KHMT", "Khoa Khoa hoc may tinh"),
]

HOC_PHAN_DATA = []
for i in range(1, 21):
    HOC_PHAN_DATA.append(
        (
            f"HP{i:03d}",
            f"Hoc phan {fake.catch_phrase()}",
            random.randint(2, 4),
            random.choice(KHOA_DATA)[0],
        )
    )

HOC_PHAN_DATA.append(("INT102", "Co so du lieu phan tan", 3, "CNTT"))

# 2. Du lieu phan manh theo site.
PHONG_HOC_DATA = {site: [] for site in SITE_CODES}
GIANG_VIEN_DATA = {site: [] for site in SITE_CODES}
SINH_VIEN_DATA = {site: [] for site in SITE_CODES}
LOP_HOC_PHAN_DATA = {site: [] for site in SITE_CODES}
LICH_HOC_DATA = {site: [] for site in SITE_CODES}

DEGREES = ["ThS", "TS", "PGS", "GS"]

for site in SITE_CODES:
    for i in range(1, 21):
        PHONG_HOC_DATA[site].append(
            (
                f"PH-{site}-{i:03d}",
                f"Phong {site}-{i}",
                random.choice([50, 80, 100, 120]),
                site,
            )
        )

    for i in range(1, 21):
        GIANG_VIEN_DATA[site].append(
            (
                f"GV-{site}-{i:03d}",
                fake.name(),
                fake.address()[:200],
                random.choice(DEGREES),
                fake.phone_number()[:20],
                random.choice(KHOA_DATA)[0],
                site,
            )
        )

    for i in range(1, 101):
        year = random.choice([2021, 2022, 2023, 2024])
        dept = random.choice(KHOA_DATA)[0]
        SINH_VIEN_DATA[site].append(
            (
                f"SV-{site}-{i:04d}",
                fake.name(),
                fake.date_of_birth(minimum_age=18, maximum_age=25),
                fake.address()[:200],
                f"D{str(year)[-2:]}CQ{dept}",
                year,
                fake.phone_number()[:20],
                dept,
                site,
            )
        )

    for i in range(1, 31):
        class_id = f"LHP-{site}-{i:03d}"
        shift = random.choice([1, 2, 3, 4])
        LOP_HOC_PHAN_DATA[site].append(
            (
                class_id,
                random.choice([1, 2]),
                2024,
                0,
                random.choice([40, 50, 60, 80]),
                shift,
                random.choice(HOC_PHAN_DATA)[0],
                random.choice(GIANG_VIEN_DATA[site])[0],
                site,
            )
        )

        # Mot lop hoc phan co the co nhieu lich hoc, moi lich hoc gan mot phong.
        session_count = random.choice([1, 2])
        days = random.sample(range(2, 8), session_count)
        rooms = random.sample(PHONG_HOC_DATA[site], session_count)
        for index, (day_of_week, room) in enumerate(zip(days, rooms), start=1):
            start_period = random.choice([1, 3, 5, 7])
            LICH_HOC_DATA[site].append(
                (
                    f"LH-{site}-{i:03d}-{index}",
                    class_id,
                    day_of_week,
                    start_period,
                    start_period + 1,
                    room[0],
                )
            )

# Lop dac biet de test dang ky dong thoi.
LOP_HOC_PHAN_DATA["HL"].append(
    ("LHP-HL-TEST", 1, 2024, 0, 1, 1, "INT102", GIANG_VIEN_DATA["HL"][0][0], "HL")
)
LICH_HOC_DATA["HL"].append(
    ("LH-HL-TEST-1", "LHP-HL-TEST", 2, 1, 2, PHONG_HOC_DATA["HL"][0][0])
)


# Nạp dữ liệu dùng chung cần nhân bản sang tất cả site.
def seed_replicated_data(conn):
    """Nạp dữ liệu dùng chung cần nhân bản sang tất cả site."""
    cursor = conn.cursor()
    execute_values(
        cursor,
        "INSERT INTO CoSo (ID, name_headquarter, address) VALUES %s ON CONFLICT DO NOTHING",
        CO_SO_DATA,
    )
    execute_values(
        cursor,
        "INSERT INTO Khoa (ID, name_department) VALUES %s ON CONFLICT DO NOTHING",
        KHOA_DATA,
    )
    execute_values(
        cursor,
        "INSERT INTO HocPhan (ID, name_subject, number_of_credit, ID_department) VALUES %s ON CONFLICT DO NOTHING",
        HOC_PHAN_DATA,
    )
    conn.commit()
    cursor.close()


# Nạp dữ liệu phân mảnh riêng cho từng site/cơ sở.
def seed_fragmented_data(conn, site_code):
    """Nạp dữ liệu phân mảnh riêng cho từng site/cơ sở."""
    cursor = conn.cursor()
    if site_code in PHONG_HOC_DATA:
        execute_values(
            cursor,
            "INSERT INTO PhongHoc (ID, name_room, capacity, ID_headquarter) VALUES %s ON CONFLICT DO NOTHING",
            PHONG_HOC_DATA[site_code],
        )
    if site_code in GIANG_VIEN_DATA:
        execute_values(
            cursor,
            "INSERT INTO GiangVien (ID, name_teacher, address_teacher, degree, phone_teacher, ID_department, ID_headquarter) VALUES %s ON CONFLICT DO NOTHING",
            GIANG_VIEN_DATA[site_code],
        )
    if site_code in SINH_VIEN_DATA:
        execute_values(
            cursor,
            "INSERT INTO SinhVien (ID, name_student, date_of_birth, address_student, formal_class, year_of_admission, phone_student, ID_department, ID_headquarter) VALUES %s ON CONFLICT DO NOTHING",
            SINH_VIEN_DATA[site_code],
        )
    if site_code in LOP_HOC_PHAN_DATA:
        execute_values(
            cursor,
            "INSERT INTO LopHocPhan (ID, semester, school_year, number_of_student, max_student, shift, ID_subject, ID_teacher, ID_headquarter) VALUES %s ON CONFLICT DO NOTHING",
            LOP_HOC_PHAN_DATA[site_code],
        )
    if site_code in LICH_HOC_DATA:
        execute_values(
            cursor,
            "INSERT INTO LichHoc (ID, ID_class, day_of_week, start_period, end_period, ID_room) VALUES %s ON CONFLICT DO NOTHING",
            LICH_HOC_DATA[site_code],
        )
    conn.commit()
    cursor.close()


# Điểm vào của module, chuẩn bị dữ liệu/giao diện rồi điều phối sang luồng nghiệp vụ phù hợp.
def main():
    """Điểm vào của module, chuẩn bị dữ liệu/giao diện rồi điều phối sang luồng nghiệp vụ phù hợp."""
    print("=======================================")
    print(" BAT DAU SINH DU LIEU MAU ")
    print("=======================================")
    for site in SITE_CODES:
        print(f"[*] Dang insert du lieu cho site: {site}...")
        conn = get_connection(site)
        try:
            seed_replicated_data(conn)
            seed_fragmented_data(conn, site)
            print(f"  -> Thanh cong: site {site}")
        except Exception as exc:
            print(f"  -> Loi tai site {site}: {exc}")
            conn.rollback()
        finally:
            conn.close()
    print("=======================================")
    print(" HOAN THANH SINH DU LIEU MAU ")


if __name__ == "__main__":
    main()
