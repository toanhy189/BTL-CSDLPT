"""Trang huy dang ky hoc phan."""

import streamlit as st

from db.queries import get_class_sections
from pages._helpers import id_options, select_site, selected_id, show_result
from services.registration_service import cancel_registration


def render_cancel_page():
    st.title("Hủy đăng ký học phần")

    student_id = st.text_input("Mã sinh viên")
    class_site = select_site("Cơ sở mở lớp", key="cancel_class_site")
    classes = get_class_sections(class_site)
    options = id_options(classes, "id", "name_subject")

    class_id = ""
    if options:
        class_id = selected_id(st.selectbox("Chọn lớp học phần", options))
    class_id = st.text_input("Hoặc nhập mã lớp học phần", value=class_id)

    if st.button("Hủy đăng ký", type="primary"):
        if not student_id.strip() or not class_id.strip():
            st.error("Vui lòng nhập đủ mã sinh viên và mã lớp")
        else:
            success, message = cancel_registration(student_id.strip(), class_site, class_id.strip())
            show_result(success, message)
