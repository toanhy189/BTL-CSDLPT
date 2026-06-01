"""Student home page."""

import streamlit as st

from api_client import api_get
from styles import SITE_LABELS, html_table, metric_card, page_title, records_count, section_title


def _active_regs(rows):
    if not isinstance(rows, list):
        return []
    return [row for row in rows if row.get("status") == "DA_DANG_KY"]


def render_student_home(token, user):
    profile = api_get("/student-profile/me", token=token)
    registrations = api_get("/student/registrations", token=token)
    schedule = api_get("/student/schedule", token=token, params={"semester": 2, "school_year": 2026})
    active_regs = _active_regs(registrations)

    student_name = profile.get("name_student") if isinstance(profile, dict) else None
    student_id = user.get("ref_id")
    site_code = user.get("id_headquarter")

    page_title(
        f"Chào mừng {student_name or student_id}",
        "Cổng sinh viên - đăng ký học phần và theo dõi thời khóa biểu.",
    )

    cols = [
        ("Mã sinh viên", student_id, "Tài khoản đăng nhập"),
        ("Cơ sở quản lý", SITE_LABELS.get(site_code, site_code), "Nơi quản lý hồ sơ"),
        ("Học phần đăng ký", len(active_regs), "Đang có hiệu lực"),
        ("Lịch học", records_count(schedule), "Kỳ 2 năm 2026"),
    ]
    metric_cols = st.columns(4)
    for col, (label, value, note) in zip(metric_cols, cols):
        with col:
            metric_card(label, value, note=note, red_value=label == "Mã sinh viên")

    section_title("Thông tin sinh viên")
    html_table(
        [profile] if isinstance(profile, dict) and not profile.get("_error") else [],
        [
            ("id", "Mã SV"),
            ("name_student", "Họ tên"),
            ("date_of_birth", "Ngày sinh"),
            ("formal_class", "Lớp"),
            ("year_of_admission", "Năm nhập học"),
            ("id_department", "Khoa"),
            ("id_headquarter", "Cơ sở"),
        ],
        limit=1,
    )
