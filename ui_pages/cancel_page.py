"""Trang Streamlit cho nghiệp vụ trang hủy đăng ký, hiển thị dữ liệu và gửi thao tác của người dùng."""

import streamlit as st

from db.queries import get_class_sections
from ui_pages._helpers import (
    id_options,
    page_title,
    section_title,
    select_site,
    selected_id,
    show_result,
)
from services.registration_service import cancel_registration


# Vẽ màn hình/khối giao diện trang hủy đăng ký và gọi API hoặc service khi người dùng thao tác.
def render_cancel_page():
    """Vẽ màn hình/khối giao diện trang hủy đăng ký và gọi API hoặc service khi người dùng thao tác."""
    page_title("🛑 Hủy đăng ký học phần", "Cập nhật trạng thái đăng ký và giảm sĩ số lớp.")

    col1, col2 = st.columns(2)
    with col1:
        student_id = st.text_input("Mã sinh viên", placeholder="VD: SV-HL-0001")
    with col2:
        class_site = select_site("Cơ sở mở lớp", key="cancel_class_site")

    classes = get_class_sections(class_site)
    options = id_options(classes, "id", "name_subject")

    section_title("Chọn lớp cần hủy")
    col3, col4 = st.columns(2)
    with col3:
        class_id = selected_id(st.selectbox("Lớp học phần", options)) if options else ""
    with col4:
        class_id = st.text_input("Hoặc nhập mã lớp", value=class_id, placeholder="VD: LHP-HL-001")

    if st.button("Hủy đăng ký", type="primary"):
        if not student_id.strip() or not class_id.strip():
            st.error("Vui lòng nhập đủ mã sinh viên và mã lớp")
        else:
            success, message = cancel_registration(student_id.strip(), class_site, class_id.strip())
            show_result(success, message)
