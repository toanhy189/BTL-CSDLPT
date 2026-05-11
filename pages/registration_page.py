"""Trang dang ky hoc phan."""

import streamlit as st

from db.queries import get_class_sections
from pages._helpers import id_options, select_site, selected_id, show_dataframe, show_result
from services.registration_service import register_course


def render_registration_page():
    st.title("Đăng ký học phần")

    student_site = select_site("Cơ sở sinh viên", key="register_student_site")
    student_id = st.text_input("Mã sinh viên")
    class_site = select_site("Cơ sở mở lớp", key="register_class_site")

    classes = get_class_sections(class_site)
    st.subheader("Danh sách lớp học phần tại cơ sở mở lớp")
    show_dataframe(classes)

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
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Học phần", row["name_subject"])
        col2.metric("Đã đăng ký", int(row["number_of_student"]))
        col3.metric("Sĩ số tối đa", int(row["max_student"]))
        col4.metric("Còn chỗ", remaining)

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
