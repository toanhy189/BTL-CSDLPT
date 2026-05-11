import psycopg2
from psycopg2.extras import execute_values
from db.connections import get_connection, SITE_CODES
from faker import Faker
import random
import sys

sys.stdout.reconfigure(encoding='utf-8')
fake = Faker('vi_VN')

# ==========================================
# 1. DỮ LIỆU NHÂN BẢN (REPLICATED DATA)
# ==========================================
CO_SO_DATA = [
    ('HL', 'Cơ sở Hòa Lạc', 'Khu CNC Hòa Lạc, Thạch Thất, HN'),
    ('NT', 'Cơ sở Ngọc Trục', 'Ngọc Trục, Nam Từ Liêm, HN'),
    ('HD', 'Cơ sở Hà Đông', 'Hà Đông, HN'),
    ('CG', 'Cơ sở Cầu Giấy', 'Cầu Giấy, HN'),
    ('HCM', 'Cơ sở Hồ Chí Minh', 'Quận 9, TP.HCM')
]

KHOA_DATA = [
    ('CNTT', 'Khoa Công nghệ thông tin'),
    ('ATTT', 'Khoa An toàn thông tin'),
    ('DTVT', 'Khoa Điện tử viễn thông'),
    ('HTTT', 'Khoa Hệ thống thông tin'),
    ('KHMT', 'Khoa Khoa học máy tính')
]

# Random 20 Học Phần chung
HOC_PHAN_DATA = []
for i in range(1, 21):
    hp_id = f'HP{i:03d}'
    name = f'Học phần {fake.catch_phrase()}'
    credits = random.randint(2, 4)
    dept_id = random.choice(KHOA_DATA)[0]
    HOC_PHAN_DATA.append((hp_id, name, credits, dept_id))

# Học phần đặc biệt để lát nữa test concurrency
HOC_PHAN_DATA.append(('INT102', 'Cơ sở dữ liệu phân tán', 3, 'CNTT'))

# ==========================================
# 2. DỮ LIỆU PHÂN MẢNH (FRAGMENTED DATA)
# ==========================================
PHONG_HOC_DATA = {site: [] for site in SITE_CODES}
GIANG_VIEN_DATA = {site: [] for site in SITE_CODES}
SINH_VIEN_DATA = {site: [] for site in SITE_CODES}
LOP_HOC_PHAN_DATA = {site: [] for site in SITE_CODES}

DEGREES = ['ThS', 'TS', 'PGS', 'GS']

for site in SITE_CODES:
    # Sinh 20 Phòng học cho từng site
    for i in range(1, 21):
        PHONG_HOC_DATA[site].append((f'PH-{site}-{i:03d}', f'Phòng {site}-{i}', random.choice([50, 80, 100, 120]), site))
    
    # Sinh 20 Giảng viên cho từng site
    for i in range(1, 21):
        GIANG_VIEN_DATA[site].append((
            f'GV-{site}-{i:03d}', 
            fake.name(), 
            fake.address()[:200], 
            random.choice(DEGREES), 
            fake.phone_number()[:20], 
            random.choice(KHOA_DATA)[0], 
            site
        ))
        
    # Sinh 100 Sinh viên cho từng site
    for i in range(1, 101):
        year = random.choice([2021, 2022, 2023, 2024])
        dept = random.choice(KHOA_DATA)[0]
        SINH_VIEN_DATA[site].append((
            f'SV-{site}-{i:04d}', 
            fake.name(), 
            fake.date_of_birth(minimum_age=18, maximum_age=25), 
            fake.address()[:200], 
            f'D{str(year)[-2:]}CQ{dept}', 
            year, 
            fake.phone_number()[:20], 
            dept, 
            site
        ))
        
    # Sinh 30 Lớp học phần cho từng site
    for i in range(1, 31):
        LOP_HOC_PHAN_DATA[site].append((
            f'LHP-{site}-{i:03d}', 
            random.choice([1, 2]), 
            2024, 
            0, # current_std
            random.choice([40, 50, 60, 80]), # max_std
            random.choice([1, 2, 3, 4]), # shift
            random.choice(HOC_PHAN_DATA)[0], # ID_subject
            random.choice(GIANG_VIEN_DATA[site])[0], # ID_teacher
            random.choice(PHONG_HOC_DATA[site])[0], # ID_room
            site
        ))

# Tạo cố tình 1 Lớp cực kỳ đặc biệt ở site HL để test Tranh chấp đồng thời (Chỉ 1 chỗ ngồi)
LOP_HOC_PHAN_DATA['HL'].append(
    ('LHP-HL-TEST', 1, 2024, 0, 1, 1, 'INT102', GIANG_VIEN_DATA['HL'][0][0], PHONG_HOC_DATA['HL'][0][0], 'HL')
)

def seed_replicated_data(conn):
    cursor = conn.cursor()
    execute_values(cursor, "INSERT INTO CoSo (ID, name_headquarter, address) VALUES %s ON CONFLICT DO NOTHING", CO_SO_DATA)
    execute_values(cursor, "INSERT INTO Khoa (ID, name_department) VALUES %s ON CONFLICT DO NOTHING", KHOA_DATA)
    execute_values(cursor, "INSERT INTO HocPhan (ID, name_subject, number_of_credit, ID_department) VALUES %s ON CONFLICT DO NOTHING", HOC_PHAN_DATA)
    conn.commit()
    cursor.close()

def seed_fragmented_data(conn, site_code):
    cursor = conn.cursor()
    if site_code in PHONG_HOC_DATA:
        execute_values(cursor, "INSERT INTO PhongHoc (ID, name_room, capacity, ID_headquarter) VALUES %s ON CONFLICT DO NOTHING", PHONG_HOC_DATA[site_code])
    if site_code in GIANG_VIEN_DATA:
        execute_values(cursor, "INSERT INTO GiangVien (ID, name_teacher, address_teacher, degree, phone_teacher, ID_department, ID_headquarter) VALUES %s ON CONFLICT DO NOTHING", GIANG_VIEN_DATA[site_code])
    if site_code in SINH_VIEN_DATA:
        execute_values(cursor, "INSERT INTO SinhVien (ID, name_student, date_of_birth, address_student, formal_class, year_of_admission, phone_student, ID_department, ID_headquarter) VALUES %s ON CONFLICT DO NOTHING", SINH_VIEN_DATA[site_code])
    if site_code in LOP_HOC_PHAN_DATA:
        execute_values(cursor, "INSERT INTO LopHocPhan (ID, semester, school_year, number_of_student, max_student, shift, ID_subject, ID_teacher, ID_room, ID_headquarter) VALUES %s ON CONFLICT DO NOTHING", LOP_HOC_PHAN_DATA[site_code])
    conn.commit()
    cursor.close()

def main():
    print("=======================================")
    print(" BẮT ĐẦU CHẠY SCRIPT SINH DỮ LIỆU FAKER ")
    print("=======================================")
    for site in SITE_CODES:
        print(f"[*] Đang kết nối và insert dữ liệu cho site: {site}...")
        conn = get_connection(site)
        try:
            seed_replicated_data(conn)
            seed_fragmented_data(conn, site)
            print(f"  -> Thành công: Đã chèn thêm 100 SV, 30 Lớp HP, 20 GV vào site {site}")
        except Exception as e:
            print(f"  -> Lỗi tại site {site}: {e}")
            conn.rollback()
        finally:
            conn.close()
    print("=======================================")
    print(" HOÀN THÀNH SINH DỮ LIỆU LỚN ! ")

if __name__ == '__main__':
    main()
