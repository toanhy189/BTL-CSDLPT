"""Module phục vụ nghiệp vụ seed data trong hệ thống đăng ký học phần phân tán."""

from datetime import date, time, timedelta
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

HOC_PHAN_DATA = [
    ("HP001", "Nhap mon lap trinh", 3, "CNTT"),
    ("HP002", "Cau truc du lieu va giai thuat", 3, "KHMT"),
    ("HP003", "Co so du lieu", 3, "HTTT"),
    ("HP004", "He quan tri co so du lieu", 3, "HTTT"),
    ("HP005", "Mang may tinh", 3, "CNTT"),
    ("HP006", "He dieu hanh", 3, "CNTT"),
    ("HP007", "Lap trinh huong doi tuong", 3, "CNTT"),
    ("HP008", "Cong nghe phan mem", 3, "CNTT"),
    ("HP009", "Phan tich thiet ke he thong", 3, "HTTT"),
    ("HP010", "Tri tue nhan tao", 3, "KHMT"),
    ("HP011", "Hoc may", 3, "KHMT"),
    ("HP012", "An toan thong tin", 3, "ATTT"),
    ("HP013", "Mat ma hoc", 3, "ATTT"),
    ("HP014", "Kien truc may tinh", 3, "DTVT"),
    ("HP015", "Lap trinh Web", 3, "CNTT"),
    ("HP016", "Lap trinh ung dung di dong", 3, "CNTT"),
    ("HP017", "Dien toan dam may", 3, "HTTT"),
    ("HP018", "Du lieu lon", 3, "KHMT"),
    ("HP019", "Khai pha du lieu", 3, "KHMT"),
    ("HP020", "Kiem thu phan mem", 3, "CNTT"),
    ("INT102", "Co so du lieu phan tan", 3, "CNTT"),
]

PERIOD_TIME = {
    1: (time(7, 0), time(7, 50)),
    2: (time(8, 0), time(8, 50)),
    3: (time(9, 0), time(9, 50)),
    4: (time(10, 0), time(10, 50)),
    5: (time(11, 0), time(11, 50)),
    6: (time(12, 0), time(12, 50)),
    7: (time(13, 0), time(13, 50)),
    8: (time(14, 0), time(14, 50)),
    9: (time(15, 0), time(15, 50)),
    10: (time(16, 0), time(16, 50)),
    11: (time(17, 0), time(17, 50)),
    12: (time(18, 0), time(18, 50)),
}
SEMESTER_START_DATE = date(2026, 4, 20)

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
        semester = 2
        school_year = 2026
        LOP_HOC_PHAN_DATA[site].append(
            (
                class_id,
                semester,
                school_year,
                0,
                random.choice([40, 50, 60, 80]),
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
            end_period = start_period + 1
            start_time = PERIOD_TIME[start_period][0]
            end_time = PERIOD_TIME[end_period][1]
            for week_number in range(1, 7):
                study_date = SEMESTER_START_DATE + timedelta(weeks=week_number - 1, days=day_of_week - 2)
                LICH_HOC_DATA[site].append(
                    (
                        f"LH-{site}-{i:03d}-{index}-W{week_number:02d}",
                        class_id,
                        study_date,
                        week_number,
                        day_of_week,
                        start_period,
                        end_period,
                        start_time,
                        end_time,
                        room[0],
                    )
                )

# Lop dac biet de test dang ky dong thoi.
LOP_HOC_PHAN_DATA["HL"].append(
    ("LHP-HL-TEST", 2, 2026, 0, 1, "INT102", GIANG_VIEN_DATA["HL"][0][0], "HL")
)
for week_number in range(1, 7):
    LICH_HOC_DATA["HL"].append(
        (
            f"LH-HL-TEST-W{week_number:02d}",
            "LHP-HL-TEST",
            SEMESTER_START_DATE + timedelta(weeks=week_number - 1),
            week_number,
            2,
            1,
            2,
            PERIOD_TIME[1][0],
            PERIOD_TIME[2][1],
            PHONG_HOC_DATA["HL"][0][0],
        )
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
            "INSERT INTO LopHocPhan (ID, semester, school_year, number_of_student, max_student, ID_subject, ID_teacher, ID_headquarter) VALUES %s ON CONFLICT DO NOTHING",
            LOP_HOC_PHAN_DATA[site_code],
        )
    if site_code in LICH_HOC_DATA:
        execute_values(
            cursor,
            "INSERT INTO LichHoc (ID, ID_class, study_date, week_number, day_of_week, start_period, end_period, start_time, end_time, ID_room) VALUES %s ON CONFLICT DO NOTHING",
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
