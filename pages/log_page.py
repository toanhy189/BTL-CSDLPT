"""Trang nhat ky thao tac."""

import streamlit as st

from services.log_service import read_logs


def render_log_page():
    st.title("Nhật ký thao tác")
    content = read_logs()
    if not content:
        st.info("Chưa có log")
    else:
        st.code(content)
