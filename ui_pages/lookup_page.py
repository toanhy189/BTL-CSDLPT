"""Trang Streamlit cho nghiệp vụ trang tra cứu, hiển thị dữ liệu và gửi thao tác của người dùng."""

import streamlit as st

from db.queries import get_registration_by_student
from ui_pages._helpers import page_title, section_title, show_dataframe


# Vẽ màn hình/khối giao diện trang tra cứu và gọi API hoặc service khi người dùng thao tác.
def render_lookup_page():
    """Vẽ màn hình/khối giao diện trang tra cứu và gọi API hoặc service khi người dùng thao tác."""
    page_title("🔎 Tra cứu kết quả đăng ký", "Tìm đăng ký của sinh viên trên toàn bộ 5 site.")
    col1, col2 = st.columns([2, 1])
    with col1:
        student_id = st.text_input("Mã sinh viên", placeholder="VD: SV-HL-0001")
    with col2:
        st.write("")
        st.write("")
        run = st.button("Tra cứu", type="primary")

    if run:
        if not student_id.strip():
            st.error("Vui lòng nhập mã sinh viên")
            return
        section_title("Kết quả tra cứu")
        df = get_registration_by_student(student_id.strip())
        show_dataframe(df, height=420)
