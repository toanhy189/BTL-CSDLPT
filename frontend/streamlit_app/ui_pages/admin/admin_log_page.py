"""Trang Streamlit cho nghiệp vụ trang nhật ký của quản trị viên, hiển thị dữ liệu và gửi thao tác của người dùng."""

import streamlit as st

from api_client import api_get
from styles import page_title, section_title


# Vẽ màn hình/khối giao diện admin nhật ký và gọi API hoặc service khi người dùng thao tác.
def render_admin_log(token):
    """Vẽ màn hình/khối giao diện admin nhật ký và gọi API hoặc service khi người dùng thao tác."""
    page_title("Nhật ký thao tác", "Theo dõi log xử lý đăng ký và mô phỏng đồng thời.")
    section_title("Log hệ thống")
    data = api_get("/concurrency/logs", token=token)
    st.code(data.get("logs", "") if not data.get("_error") else data.get("message"))
