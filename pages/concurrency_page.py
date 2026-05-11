"""Trang mo phong dang ky dong thoi."""

import streamlit as st

from db.queries import get_class_sections
from pages._helpers import id_options, select_site, selected_id, show_dataframe
from services.log_service import read_log_lines, write_concurrent_result
from services.registration_service import simulate_concurrent_registration


def _parse_students(raw_text):
    students = []
    for line in raw_text.splitlines():
        line = line.strip()
        if not line or "," not in line:
            continue
        student_id, site_code = [part.strip() for part in line.split(",", 1)]
        if student_id and site_code:
            students.append({"id_student": student_id, "id_student_headquarter": site_code})
    return students


def render_concurrency_page():
    st.title("Mô phỏng đăng ký đồng thời")

    class_site = select_site("Cơ sở mở lớp", key="concurrency_class_site")
    classes = get_class_sections(class_site)
    options = id_options(classes, "id", "name_subject")
    if options:
        class_id = selected_id(st.selectbox("Chọn lớp học phần", options))
    else:
        class_id = st.text_input("Mã lớp học phần")

    raw_students = st.text_area(
        "Danh sách sinh viên, mỗi dòng: MA_SV,SITE",
        value="SV-HL-0001,HL\nSV-HL-0002,HL\nSV-HL-0003,HL\nSV-HL-0004,HL\nSV-HL-0005,HL",
        height=140,
    )

    if st.button("Chạy mô phỏng", type="primary"):
        students = _parse_students(raw_students)
        if not class_id or not students:
            st.error("Vui lòng chọn lớp và nhập danh sách sinh viên hợp lệ")
            return
        df = simulate_concurrent_registration(class_site, class_id, students)
        write_concurrent_result(df)
        success_count = int(df["success"].sum()) if not df.empty else 0
        col1, col2 = st.columns(2)
        col1.metric("Thành công", success_count)
        col2.metric("Thất bại", max(len(df) - success_count, 0))
        show_dataframe(df)

    st.subheader("Log gần nhất")
    st.code("\n".join(read_log_lines(80)) or "Chưa có log")
