"""Student profile page."""

from api_client import api_get
import streamlit as st
from styles import SITE_LABELS, html_table, metric_card, page_title, section_title


def render_student_profile(token):
    page_title("Hồ sơ cá nhân", "Thông tin sinh viên được đọc từ site quản lý hồ sơ.")
    data = api_get("/student-profile/me", token=token)
    if isinstance(data, dict) and data.get("_error"):
        metric_card("Không tải được hồ sơ", data.get("message"), red_value=True)
        return

    site_code = data.get("id_headquarter") if isinstance(data, dict) else ""
    cols = st.columns(3)
    with cols[0]:
        metric_card("Mã sinh viên", data.get("id"), red_value=True)
    with cols[1]:
        metric_card("Cơ sở", SITE_LABELS.get(site_code, site_code))
    with cols[2]:
        metric_card("Khoa", data.get("id_department"))

    section_title("Thông tin sinh viên")
    html_table(
        [data] if data else [],
        [
            ("id", "Mã SV"),
            ("name_student", "Họ tên"),
            ("date_of_birth", "Ngày sinh"),
            ("formal_class", "Lớp"),
            ("year_of_admission", "Năm nhập học"),
            ("phone_student", "Điện thoại"),
            ("id_department", "Khoa"),
            ("id_headquarter", "Cơ sở"),
        ],
        limit=1,
    )

    section_title("Thông tin liên hệ")
    html_table(
        [data] if data else [],
        [
            ("address_student", "Địa chỉ"),
            ("phone_student", "Điện thoại"),
        ],
        limit=1,
    )
