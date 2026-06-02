"""Trang chủ giảng viên, hiển thị thống kê nhanh và lối tắt thao tác."""

import streamlit as st

from api_client import api_get
from styles import metric_card, page_title, section_title


# Vẽ trang chủ giảng viên và lấy số liệu tổng quan từ API.
def render_teacher_home(token):
    """Vẽ trang chủ giảng viên và lấy số liệu tổng quan từ API."""
    page_title("Trang chủ giảng viên", "Tổng quan lớp học phần phụ trách.")
    data = api_get("/teacher/statistics", token=token)
    if data.get("_error"):
        st.error(data.get("message"))
        return

    cols = st.columns(3)
    with cols[0]:
        metric_card("Số lớp phụ trách", data.get("class_count", 0), icon="▤", accent="red")
    with cols[1]:
        metric_card("Tổng sinh viên", data.get("total_students", 0), icon="◌", accent="green")
    with cols[2]:
        metric_card("Cơ sở", data.get("site", ""), icon="▥", accent="blue")

    section_title("Lối tắt")
    st.info("Chọn Lớp học phần phụ trách hoặc Lịch dạy ở menu bên trái để xem chi tiết.")
