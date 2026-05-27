"""Trang Streamlit cho nghiệp vụ nhật ký page, hiển thị dữ liệu và gửi thao tác của người dùng."""

import streamlit as st

from services.log_service import read_logs
from ui_pages._helpers import page_title, section_title


# Vẽ màn hình/khối giao diện nhật ký page và gọi API hoặc service khi người dùng thao tác.
def render_log_page():
    """Vẽ màn hình/khối giao diện nhật ký page và gọi API hoặc service khi người dùng thao tác."""
    page_title("📜 Nhật ký thao tác", "Theo dõi thao tác đăng ký, hủy đăng ký và mô phỏng đồng thời.")
    section_title("Nội dung log")
    content = read_logs()
    if not content:
        st.info("Chưa có log")
    else:
        st.code(content)
