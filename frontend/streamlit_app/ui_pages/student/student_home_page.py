"""Trang Streamlit cho nghiệp vụ trang chủ sinh viên, hiển thị dữ liệu và gửi thao tác của người dùng."""

import streamlit as st

from styles import metric_card, page_title, section_title


# Vẽ màn hình/khối giao diện sinh viên home và gọi API hoặc service khi người dùng thao tác.
def render_student_home(user):
    """Vẽ màn hình/khối giao diện sinh viên home và gọi API hoặc service khi người dùng thao tác."""
    page_title("Trang chủ sinh viên", "Cổng đăng ký học phần cá nhân.")

    cols = st.columns(3)
    with cols[0]:
        metric_card("Mã sinh viên", user.get("ref_id"), icon="▣", accent="red", red_value=True)
    with cols[1]:
        metric_card("Cơ sở", user.get("id_headquarter"), icon="▥", accent="blue")
    with cols[2]:
        metric_card("Vai trò", "Sinh viên", icon="○", accent="green")

    section_title("Lối tắt")
    st.info("Chọn Đăng ký học phần, Kết quả đăng ký hoặc Thời khóa biểu ở menu bên trái để thao tác.")
