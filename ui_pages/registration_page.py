"""Trang Streamlit cho nghiệp vụ trang đăng ký học phần, hiển thị dữ liệu và gửi thao tác của người dùng."""

import streamlit as st

from db.queries import get_class_sections
from ui_pages._helpers import (
    id_options,
    metric_card,
    page_title,
    section_title,
    select_site,
    selected_id,
    show_dataframe,
    show_result,
)
from services.registration_service import register_course


# Vẽ màn hình/khối giao diện trang đăng ký học phần và gọi API hoặc service khi người dùng thao tác.
def render_registration_page():
    """Vẽ màn hình/khối giao diện trang đăng ký học phần và gọi API hoặc service khi người dùng thao tác."""
    page_title("📝 Đăng ký học phần", "Sinh viên có thể đăng ký lớp học phần ở cơ sở khác.")

    filter_col1, filter_col2, filter_col3 = st.columns([1.2, 1.2, 1.6])
    with filter_col1:
        student_site = select_site("Cơ sở sinh viên", key="register_student_site")
    with filter_col2:
        class_site = select_site("Cơ sở mở lớp", key="register_class_site")
    with filter_col3:
        student_id = st.text_input("Mã sinh viên", placeholder="VD: SV-HL-0001")

    classes = get_class_sections(class_site)
    section_title("Danh sách lớp học phần", f"Dữ liệu lớp mở tại site {class_site}.")
    show_dataframe(classes, height=360)

    options = id_options(classes, "id", "name_subject")
    if not options:
        st.info("Chưa có lớp học phần để đăng ký")
        return

    class_option = st.selectbox("Chọn lớp học phần", options)
    class_id = selected_id(class_option)
    selected_class = classes[classes["id"] == class_id]
    if not selected_class.empty:
        row = selected_class.iloc[0]
        remaining = int(row["max_student"]) - int(row["number_of_student"])
        cols = st.columns(4)
        with cols[0]:
            metric_card("Học phần", row["name_subject"])
        with cols[1]:
            metric_card("Đã đăng ký", int(row["number_of_student"]))
        with cols[2]:
            metric_card("Sĩ số tối đa", int(row["max_student"]))
        with cols[3]:
            metric_card("Còn chỗ", remaining)

    if st.button("Đăng ký", type="primary"):
        if not student_id.strip():
            st.error("Vui lòng nhập mã sinh viên")
        else:
            success, message = register_course(
                student_id.strip(),
                student_site,
                class_site,
                class_id,
            )
            show_result(success, message)
