"""Truy vấn báo cáo phân tán, đọc dữ liệu từ nhiều site rồi gắn thông tin cơ sở."""

import pandas as pd

from backend.core.config import SITE_CODES, SITE_NAMES
from backend.db.queries import read_sql
from backend.services.log_service import write_log


# Gắn mã site và tên site vào kết quả để biết dữ liệu đến từ cơ sở nào.
def _add_site(df, site_code):
    df = df.copy()
    df["site_code"] = site_code
    df["site_name"] = SITE_NAMES.get(site_code, site_code)
    return df


# Chạy cùng một truy vấn trên toàn bộ site và ghép các DataFrame không rỗng.
def _attach_site_status(df, available_sites, failed_sites):
    df.attrs["available_sites"] = available_sites
    df.attrs["failed_sites"] = failed_sites
    if failed_sites:
        labels = ", ".join(SITE_NAMES.get(site, site) for site in failed_sites)
        df.attrs["warning"] = f"Ket qua chua bao gom site: {labels}"
    else:
        df.attrs["warning"] = None
    return df


def _copy_site_status(df, source_df):
    return _attach_site_status(
        df,
        source_df.attrs.get("available_sites", []),
        source_df.attrs.get("failed_sites", []),
    )


def _all_sites(query, params=None):
    """Chạy cùng một truy vấn trên toàn bộ site và ghép các DataFrame không rỗng."""
    frames = []
    available_sites = []
    failed_sites = []
    for site_code in SITE_CODES:
        try:
            df = read_sql(site_code, query, params)
            available_sites.append(site_code)
            if not df.empty:
                frames.append(_add_site(df, site_code))
        except Exception as exc:
            failed_sites.append(site_code)
            write_log(f"SITE_DOWN site={site_code} action=DISTRIBUTED_QUERY error={exc}")
    if not frames:
        return _attach_site_status(pd.DataFrame(), available_sites, failed_sites)
    return _attach_site_status(pd.concat(frames, ignore_index=True), available_sites, failed_sites)


# Thống kê số lượt đăng ký học phần theo từng cơ sở mở lớp.
def thong_ke_dang_ky_theo_co_so():
    df = _all_sites(
        """
        SELECT l.id_headquarter, COUNT(d.id_student) AS so_luot_dang_ky
        FROM lophocphan l
        LEFT JOIN dangky d ON l.id = d.id_class AND d.status = 'DA_DANG_KY'
        GROUP BY l.id_headquarter;
        """
    )
    if df.empty:
        return df
    result = (
        df.groupby(["id_headquarter", "site_name"], as_index=False, dropna=False)["so_luot_dang_ky"]
        .sum()
        .sort_values(["id_headquarter", "site_name"], ignore_index=True)
    )
    return _copy_site_status(result, df)


# Tìm các học phần có nhiều lượt đăng ký nhất trên toàn hệ thống.
def hoc_phan_dang_ky_nhieu_nhat():
    df = _all_sites(
        """
        SELECT hp.id AS id_subject, hp.name_subject, COUNT(d.id_student) AS so_luot
        FROM hocphan hp
        JOIN lophocphan l ON hp.id = l.id_subject
        LEFT JOIN dangky d ON l.id = d.id_class AND d.status = 'DA_DANG_KY'
        GROUP BY hp.id, hp.name_subject;
        """
    )
    if df.empty:
        return df
    result = (
        df.groupby(["id_subject", "name_subject"], as_index=False, dropna=False)["so_luot"]
        .sum()
        .sort_values("so_luot", ascending=False, ignore_index=True)
    )
    return _copy_site_status(result, df)


# Liệt kê sinh viên đăng ký lớp học phần khác cơ sở quản lý hồ sơ của mình.
def sinh_vien_dang_ky_cheo_co_so():
    return _all_sites(
        """
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
    )


# Tính tỷ lệ lấp đầy, sức chứa và số chỗ còn lại của từng lớp học phần.
def ty_le_lap_day_lop_hoc_phan():
    return _all_sites(
        """
        SELECT
            l.id AS id_class,
            l.id_headquarter,
            l.id_subject,
            hp.name_subject,
            l.number_of_student,
            l.max_student,
            (l.max_student - l.number_of_student) AS so_cho_con_lai,
            ROUND((l.number_of_student::numeric / NULLIF(l.max_student, 0)) * 100, 2) AS ty_le_lap_day
        FROM lophocphan l
        JOIN hocphan hp ON l.id_subject = hp.id;
        """
    )


# Đếm số lớp học phần đang mở theo từng cơ sở.
def thong_ke_so_lop_theo_co_so():
    df = _all_sites(
        """
        SELECT id_headquarter, COUNT(id) AS so_lop_mo
        FROM lophocphan
        GROUP BY id_headquarter;
        """
    )
    if df.empty:
        return df
    result = (
        df.groupby(["id_headquarter", "site_name"], as_index=False, dropna=False)["so_lop_mo"]
        .sum()
        .sort_values(["id_headquarter", "site_name"], ignore_index=True)
    )
    return _copy_site_status(result, df)


# Đếm số sinh viên thuộc từng cơ sở quản lý.
def thong_ke_sinh_vien_theo_co_so():
    df = _all_sites(
        """
        SELECT id_headquarter, COUNT(id) AS so_sinh_vien
        FROM sinhvien
        GROUP BY id_headquarter;
        """
    )
    if df.empty:
        return df
    result = (
        df.groupby(["id_headquarter", "site_name"], as_index=False, dropna=False)["so_sinh_vien"]
        .sum()
        .sort_values(["id_headquarter", "site_name"], ignore_index=True)
    )
    return _copy_site_status(result, df)


# Gom danh sách lớp học phần toàn trường kèm cơ sở, học phần, sĩ số và phòng học.
def danh_sach_lop_hoc_phan_toan_truong():
    return _all_sites(
        """
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
            l.id, l.id_headquarter, l.id_subject, hp.name_subject,
            l.semester, l.school_year, l.number_of_student, l.max_student;
        """
    )
