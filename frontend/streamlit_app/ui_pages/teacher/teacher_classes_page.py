"""Teacher class-section page."""

import streamlit as st

from api_client import api_get
from styles import html_table, metric_card, page_title, records_count, section_title, sum_field


def render_teacher_classes(token):
    page_title("Lớp học phần phụ trách", "Theo dõi lớp giảng dạy và danh sách sinh viên theo từng lớp.")

    classes = api_get("/teacher/classes", token=token)
    schedule = api_get("/teacher/schedule", token=token, params={"semester": 2, "school_year": 2026})

    cols = st.columns(4)
    with cols[0]:
        metric_card("Số lớp đang dạy", records_count(classes), red_value=True)
    with cols[1]:
        metric_card("Tổng sinh viên", int(sum_field(classes, "number_of_student")))
    with cols[2]:
        sites = len({row.get("id_headquarter") for row in classes}) if isinstance(classes, list) else 0
        metric_card("Số cơ sở tham gia", sites)
    with cols[3]:
        metric_card("Buổi dạy", records_count(schedule), note="Kỳ 2 năm 2026")

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
        limit=None,
        progress=("number_of_student", "max_student"),
    )

    section_title("Danh sách sinh viên theo lớp")
    rows = classes if isinstance(classes, list) else []
    if not rows:
        st.info("Chưa có lớp phụ trách.")
        return

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
        limit=None,
        status_columns={"status"},
    )
