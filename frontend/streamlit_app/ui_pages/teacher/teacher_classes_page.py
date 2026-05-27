"""Trang Streamlit cho nghiệp vụ trang lớp phụ trách của giảng viên, hiển thị dữ liệu và gửi thao tác của người dùng."""

import streamlit as st

from api_client import api_get
from styles import html_table, metric_card, page_title, records_count, schedule_grid, section_title, sum_field


# Vẽ màn hình/khối giao diện lớp giảng viên phụ trách và gọi API hoặc service khi người dùng thao tác.
def render_teacher_classes(token):
    """Vẽ màn hình/khối giao diện lớp giảng viên phụ trách và gọi API hoặc service khi người dùng thao tác."""
    page_title("Lớp học phần phụ trách", "Theo dõi lớp giảng dạy, sĩ số và lịch trong tuần.")

    classes = api_get("/teacher/classes", token=token)
    schedule = api_get("/teacher/schedule", token=token)

    cols = st.columns(4)
    with cols[0]:
        metric_card("Số lớp đang dạy", records_count(classes), icon="▤", accent="red")
    with cols[1]:
        metric_card("Tổng sinh viên", int(sum_field(classes, "number_of_student")), icon="◌", accent="green")
    with cols[2]:
        sites = len({row.get("id_headquarter") for row in classes}) if isinstance(classes, list) else 0
        metric_card("Số cơ sở tham gia", sites, icon="▥", accent="blue")
    with cols[3]:
        metric_card("Tiết dạy tuần này", records_count(schedule), icon="▦", accent="orange")

    section_title("Danh sách lớp học phần phụ trách")
    html_table(
        classes,
        [
            ("id", "Mã lớp HP"),
            ("name_subject", "Học phần"),
            ("id_headquarter", "Cơ sở"),
            ("semester", "Học kỳ"),
            ("school_year", "Năm học"),
            ("number_of_student", "Sĩ số"),
            ("max_student", "Tối đa"),
            ("__progress__", "Tỷ lệ"),
        ],
        limit=8,
        progress=("number_of_student", "max_student"),
    )

    st.divider()
    left, right = st.columns([0.48, 0.52], gap="medium")
    with left:
        schedule_grid(schedule, "Lịch dạy trong tuần")
    with right:
        section_title("Danh sách sinh viên theo lớp")
        rows = classes if isinstance(classes, list) else []
        if rows:
            selected = st.selectbox(
                "Chọn lớp",
                rows,
                format_func=lambda row: f"{row.get('id')} - {row.get('name_subject')}",
            )
            students = api_get(f"/teacher/classes/{selected.get('id')}/students", token=token)
            html_table(
                students,
                [
                    ("id_student", "MSSV"),
                    ("id_student_headquarter", "Cơ sở SV"),
                    ("name_subject", "Học phần"),
                    ("registration_date", "Ngày đăng ký"),
                    ("status", "Trạng thái"),
                ],
                limit=8,
                status_columns={"status"},
            )
        else:
            st.info("Chưa có lớp phụ trách.")
