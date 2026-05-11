"""Trang tra cuu ket qua dang ky."""

import streamlit as st

from db.queries import get_registration_by_student
from pages._helpers import show_dataframe


def render_lookup_page():
    st.title("Tra cứu kết quả đăng ký")
    student_id = st.text_input("Mã sinh viên")

    if st.button("Tra cứu", type="primary"):
        if not student_id.strip():
            st.error("Vui lòng nhập mã sinh viên")
            return
        df = get_registration_by_student(student_id.strip())
        show_dataframe(df)
