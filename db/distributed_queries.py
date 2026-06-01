"""Truy vấn phân tán của bản Streamlit cũ, gom dữ liệu từ nhiều site thành DataFrame."""

import warnings

import pandas as pd

from db.connections import SITE_CODES, get_connection


SITE_NAMES = {
    "HL": "Hòa Lạc",
    "NT": "Ngọc Trục",
    "HD": "Hà Đông",
    "CG": "Cầu Giấy",
    "HCM": "TP.HCM",
}

ALLOWED_TABLES = {
    "coso",
    "khoa",
    "hocphan",
    "phonghoc",
    "giangvien",
    "sinhvien",
    "lophocphan",
    "lichhoc",
    "dangky",
}


# Đổi mã site sang tên hiển thị thân thiện trên giao diện.
def get_site_display_name(site_code):
    return SITE_NAMES.get(site_code, site_code)


# Bổ sung cột site_code và site_name sau khi đọc dữ liệu từ một site.
def _add_site_columns(df, site_code):

    df = df.copy()
    df["site_code"] = site_code
    df["site_name"] = get_site_display_name(site_code)
    return df


# Ghép các DataFrame không rỗng thành một bảng kết quả chung.
def _concat_frames(frames):
  
    non_empty_frames = [frame for frame in frames if frame is not None and not frame.empty]
    if not non_empty_frames:
        return pd.DataFrame()
    return pd.concat(non_empty_frames, ignore_index=True)


# Chạy cùng một truy vấn trên toàn bộ site rồi gom kết quả.
def _read_all_sites_query(query, params=None):
    """Chạy cùng một truy vấn trên toàn bộ site rồi gom kết quả."""
    frames = []
    for site_code in SITE_CODES:
        df = read_query(site_code, query, params)
        if not df.empty:
            frames.append(df)
    return _concat_frames(frames)


# Đọc dữ liệu bằng một câu SQL trên site được chọn và gắn thông tin site.
def read_query(site_code, query, params=None):
    
    conn = None
    try:
        conn = get_connection(site_code)
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message="pandas only supports SQLAlchemy connectable.*",
                category=UserWarning,
            )
            df = pd.read_sql(query, conn, params=params)
        return _add_site_columns(df, site_code)
    except Exception as exc:
        print(f"[{site_code}] Loi khi truy van: {exc}")
        return pd.DataFrame()
    finally:
        if conn is not None:
            conn.close()


# Đọc toàn bộ một bảng hợp lệ tại site được chọn để phục vụ quản trị nhanh.
def read_table(site_code, table_name):
  
    normalized_table = table_name.strip().lower()
    if normalized_table not in ALLOWED_TABLES:
        print(f"[{site_code}] Bang khong hop le: {table_name}")
        return pd.DataFrame()

    return read_query(site_code, f"SELECT * FROM {normalized_table};")


# Đọc cùng một bảng từ tất cả site rồi ghép thành dữ liệu toàn hệ thống.
def read_all_sites(table_name):
   
    frames = []
    for site_code in SITE_CODES:
        df = read_table(site_code, table_name)
        if not df.empty:
            frames.append(df)
    return _concat_frames(frames)


# Thống kê số lượt đăng ký học phần theo từng cơ sở mở lớp.
def thong_ke_dang_ky_theo_co_so():
    
    query = """
        SELECT
            l.id_headquarter,
            COUNT(d.id_student) AS so_luot_dang_ky
        FROM lophocphan l
        LEFT JOIN dangky d
            ON l.id = d.id_class
           AND d.status = 'DA_DANG_KY'
        GROUP BY l.id_headquarter;
    """
    df = _read_all_sites_query(query)
    if df.empty:
        return pd.DataFrame()

    return (
        df.groupby(["id_headquarter", "site_name"], as_index=False, dropna=False)[
            "so_luot_dang_ky"
        ]
        .sum()
        .sort_values(["id_headquarter", "site_name"], ignore_index=True)
    )


# Tìm các học phần có nhiều lượt đăng ký nhất trên toàn hệ thống.
def hoc_phan_dang_ky_nhieu_nhat():
   
    query = """
        SELECT
            hp.id AS id_subject,
            hp.name_subject,
            COUNT(d.id_student) AS so_luot
        FROM hocphan hp
        JOIN lophocphan l ON hp.id = l.id_subject
        LEFT JOIN dangky d
            ON l.id = d.id_class
           AND d.status = 'DA_DANG_KY'
        GROUP BY hp.id, hp.name_subject;
    """
    df = _read_all_sites_query(query)
    if df.empty:
        return pd.DataFrame()

    return (
        df.groupby(["id_subject", "name_subject"], as_index=False, dropna=False)[
            "so_luot"
        ]
        .sum()
        .sort_values("so_luot", ascending=False, ignore_index=True)
    )


# Liệt kê sinh viên đăng ký lớp học phần khác cơ sở quản lý hồ sơ của mình.
def sinh_vien_dang_ky_cheo_co_so():
    
    query = """
        SELECT
            d.id_student,
            d.id_student_headquarter AS student_headquarter,
            d.id_class,
            l.id_headquarter AS class_headquarter,
            d.registration_date,
            d.status
        FROM dangky d
        JOIN lophocphan l ON d.id_class = l.id
        WHERE d.id_student_headquarter <> l.id_headquarter
          AND d.status = 'DA_DANG_KY';
    """
    df = _read_all_sites_query(query)
    if df.empty:
        return pd.DataFrame()

    columns = [
        "id_student",
        "student_headquarter",
        "id_class",
        "class_headquarter",
        "registration_date",
        "status",
        "site_code",
        "site_name",
    ]
    return df[columns].sort_values(
        ["student_headquarter", "id_student", "id_class"], ignore_index=True
    )


# Tính tỷ lệ lấp đầy, sức chứa và số chỗ còn lại của từng lớp học phần.
def ty_le_lap_day_lop_hoc_phan():
    
    query = """
        SELECT
            l.id AS id_class,
            l.id_headquarter,
            l.id_subject,
            hp.name_subject,
            l.number_of_student,
            l.max_student,
            (l.max_student - l.number_of_student) AS so_cho_con_lai,
            ROUND(
                (l.number_of_student::numeric / NULLIF(l.max_student, 0)) * 100,
                2
            ) AS ty_le_lap_day
        FROM lophocphan l
        JOIN hocphan hp ON l.id_subject = hp.id;
    """
    df = _read_all_sites_query(query)
    if df.empty:
        return pd.DataFrame()

    columns = [
        "id_class",
        "id_headquarter",
        "site_code",
        "site_name",
        "id_subject",
        "name_subject",
        "number_of_student",
        "max_student",
        "so_cho_con_lai",
        "ty_le_lap_day",
    ]
    return df[columns].sort_values(["id_headquarter", "id_class"], ignore_index=True)


# Đếm số lớp học phần đang mở theo từng cơ sở.
def thong_ke_so_lop_theo_co_so():
    
    query = """
        SELECT
            id_headquarter,
            COUNT(id) AS so_lop_mo
        FROM lophocphan
        GROUP BY id_headquarter;
    """
    df = _read_all_sites_query(query)
    if df.empty:
        return pd.DataFrame()

    return (
        df.groupby(["id_headquarter", "site_name"], as_index=False, dropna=False)[
            "so_lop_mo"
        ]
        .sum()
        .sort_values(["id_headquarter", "site_name"], ignore_index=True)
    )


# Đếm số sinh viên thuộc từng cơ sở quản lý.
def thong_ke_sinh_vien_theo_co_so():
    
    query = """
        SELECT
            id_headquarter,
            COUNT(id) AS so_sinh_vien
        FROM sinhvien
        GROUP BY id_headquarter;
    """
    df = _read_all_sites_query(query)
    if df.empty:
        return pd.DataFrame()

    return (
        df.groupby(["id_headquarter", "site_name"], as_index=False, dropna=False)[
            "so_sinh_vien"
        ]
        .sum()
        .sort_values(["id_headquarter", "site_name"], ignore_index=True)
    )


# Gom danh sách lớp học phần toàn trường kèm cơ sở, học phần, sĩ số và phòng học.
def danh_sach_lop_hoc_phan_toan_truong():
    
    query = """
        SELECT
            l.id AS id_class,
            l.id_headquarter,
            l.id_subject,
            hp.name_subject,
            l.semester,
            l.school_year,
            l.number_of_student,
            l.max_student,
            STRING_AGG(DISTINCT lh.id_room, ', ' ORDER BY lh.id_room) AS id_rooms
        FROM lophocphan l
        JOIN hocphan hp ON l.id_subject = hp.id
        LEFT JOIN lichhoc lh ON lh.id_class = l.id
        GROUP BY
            l.id,
            l.id_headquarter,
            l.id_subject,
            hp.name_subject,
            l.semester,
            l.school_year,
            l.number_of_student,
            l.max_student;
    """
    df = _read_all_sites_query(query)
    if df.empty:
        return pd.DataFrame()

    columns = [
        "id_class",
        "id_headquarter",
        "site_code",
        "site_name",
        "id_subject",
        "name_subject",
        "semester",
        "school_year",
        "number_of_student",
        "max_student",
        "id_rooms",
    ]
    return df[columns].sort_values(["id_headquarter", "id_class"], ignore_index=True)
