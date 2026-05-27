"""Trang Streamlit cho nghiệp vụ trang tra cứu đăng ký của sinh viên, hiển thị dữ liệu và gửi thao tác của người dùng."""

import streamlit as st

from api_client import api_get
from styles import html_table, metric_card, page_title, records_count, schedule_grid, section_title


# Vẽ màn hình/khối giao diện sinh viên lookup và gọi API hoặc service khi người dùng thao tác.
def render_student_lookup(token):
    """Vẽ màn hình/khối giao diện sinh viên lookup và gọi API hoặc service khi người dùng thao tác."""
    page_title("Kết quả đăng ký", "Theo dõi danh sách học phần đã đăng ký và thời khóa biểu.")

    cols = st.columns([0.25, 0.25, 0.25, 0.25])
    with cols[0]:
        st.selectbox("Học kỳ", ["Học kỳ 1", "Học kỳ 2", "Học kỳ 3"], index=1)
    with cols[1]:
        st.selectbox("Năm học", ["2024 - 2025", "2025 - 2026"], index=0)
    with cols[2]:
        st.selectbox("Cơ sở", ["Tất cả cơ sở", "Cơ sở Hà Nội", "Cơ sở Đà Nẵng", "Cơ sở TP. Hồ Chí Minh"])
    with cols[3]:
        st.write("")
        if st.button("Làm mới", use_container_width=True):
            st.rerun()

    registrations = api_get("/student/registrations", token=token)
    schedule = api_get("/student/schedule", token=token)

    metric_cols = st.columns(4)
    with metric_cols[0]:
        metric_card("Số học phần đã đăng ký", records_count(registrations), icon="▤", accent="red", red_value=True)
    with metric_cols[1]:
        metric_card("Tổng số tín chỉ", records_count(registrations) * 3, icon="▱", accent="orange", red_value=True)
    with metric_cols[2]:
        cross_site = sum(1 for row in registrations if isinstance(registrations, list) and row.get("class_headquarter") != row.get("id_student_headquarter"))
        metric_card("Số môn chéo cơ sở", cross_site, icon="⇄", accent="blue", red_value=True)
    with metric_cols[3]:
        metric_card("Trạng thái đăng ký", "Thành công", icon="✓", accent="green", red_value=True)

    section_title("Danh sách học phần đã đăng ký")
    html_table(
        registrations,
        [
            ("id_class", "Mã lớp"),
            ("name_subject", "Tên học phần"),
            ("class_headquarter", "Cơ sở mở lớp"),
            ("registration_date", "Ngày đăng ký"),
            ("status", "Trạng thái"),
            ("site_name", "Site xử lý"),
        ],
        limit=None,
        status_columns={"status"},
    )

    st.divider()
    schedule_grid(schedule, "Thời khóa biểu")
