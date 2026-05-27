"""Trang Streamlit cho nghiệp vụ trang thống kê lớp của giảng viên, hiển thị dữ liệu và gửi thao tác của người dùng."""

import streamlit as st

from api_client import api_get
from styles import metric_card, page_title


# Vẽ màn hình/khối giao diện giảng viên stats và gọi API hoặc service khi người dùng thao tác.
def render_teacher_stats(token):
    """Vẽ màn hình/khối giao diện giảng viên stats và gọi API hoặc service khi người dùng thao tác."""
    page_title("Thống kê lớp", "Tổng hợp nhanh tình hình lớp học phần phụ trách.")
    data = api_get("/teacher/statistics", token=token)
    if data.get("_error"):
        metric_card("Lỗi", data.get("message"), icon="!", accent="red")
    else:
        cols = st.columns(3)
        with cols[0]:
            metric_card("Số lớp", data.get("class_count", 0), icon="▤", accent="red")
        with cols[1]:
            metric_card("Tổng sinh viên", data.get("total_students", 0), icon="◌", accent="green")
        with cols[2]:
            metric_card("Site", data.get("site", ""), icon="▥", accent="blue")
