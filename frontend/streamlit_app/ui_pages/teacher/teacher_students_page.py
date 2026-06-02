"""Trang giảng viên tra cứu danh sách sinh viên theo lớp học phần."""

import streamlit as st

from api_client import api_get
from styles import html_table, page_title, section_title


# Vẽ trang tra cứu sinh viên trong lớp và gọi API khi người dùng nhập mã lớp.
def render_teacher_students(token):
    """Vẽ trang tra cứu sinh viên trong lớp và gọi API khi người dùng nhập mã lớp."""
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
