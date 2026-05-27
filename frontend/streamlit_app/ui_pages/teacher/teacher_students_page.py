"""Trang Streamlit cho nghiệp vụ trang sinh viên trong lớp của giảng viên, hiển thị dữ liệu và gửi thao tác của người dùng."""

import streamlit as st

from api_client import api_get
from styles import html_table, page_title, section_title


# Vẽ màn hình/khối giao diện giảng viên sinh viên và gọi API hoặc service khi người dùng thao tác.
def render_teacher_students(token):
    """Vẽ màn hình/khối giao diện giảng viên sinh viên và gọi API hoặc service khi người dùng thao tác."""
    page_title("Danh sách sinh viên", "Tra cứu sinh viên đăng ký theo lớp học phần.")
    class_id = st.text_input("Mã lớp học phần", placeholder="Nhập mã lớp học phần")
    if st.button("Xem danh sách"):
        section_title("Sinh viên đăng ký lớp")
        html_table(
            api_get(f"/teacher/classes/{class_id}/students", token=token),
            [
                ("id_student", "MSSV"),
                ("id_student_headquarter", "Cơ sở SV"),
                ("id_class", "Mã lớp"),
                ("name_subject", "Học phần"),
                ("registration_date", "Ngày đăng ký"),
                ("status", "Trạng thái"),
            ],
            limit=None,
            status_columns={"status"},
        )
