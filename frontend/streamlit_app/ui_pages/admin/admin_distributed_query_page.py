"""Trang Streamlit cho nghiệp vụ trang báo cáo phân tán của quản trị viên, hiển thị dữ liệu và gửi thao tác của người dùng."""

import pandas as pd
import streamlit as st

from api_client import api_get
from styles import SITE_LABELS, dataframe, html_table, metric_card, page_title, records_count, section_title, sum_field


QUERIES = {
    "Đăng ký theo cơ sở": "/distributed/registration-by-site",
    "Top học phần": "/distributed/top-courses",
    "Đăng ký chéo cơ sở": "/distributed/cross-site-students",
    "Tỷ lệ lấp đầy": "/distributed/fill-rate",
    "Số lớp theo cơ sở": "/distributed/classes-by-site",
    "Số sinh viên theo cơ sở": "/distributed/students-by-site",
}


# Hàm hỗ trợ chuẩn hóa/lọc/chuẩn bị dữ liệu site names trước khi hiển thị hoặc xử lý.
def _site_names(rows):
    """Hàm hỗ trợ chuẩn hóa/lọc/chuẩn bị dữ liệu site names trước khi hiển thị hoặc xử lý."""
    if not isinstance(rows, list):
        return rows
    result = []
    for row in rows:
        item = dict(row)
        code = item.get("id_headquarter") or item.get("site_code")
        item["site_label"] = SITE_LABELS.get(code, item.get("site_name", code))
        result.append(item)
    return result


# Hàm hỗ trợ chuẩn hóa/lọc/chuẩn bị dữ liệu avg fill trước khi hiển thị hoặc xử lý.
def _avg_fill(rows):
    """Hàm hỗ trợ chuẩn hóa/lọc/chuẩn bị dữ liệu avg fill trước khi hiển thị hoặc xử lý."""
    if not isinstance(rows, list) or not rows:
        return 0
    return sum(float(row.get("ty_le_lap_day") or 0) for row in rows) / len(rows)


# Vẽ màn hình/khối giao diện admin truy vấn phân tán và gọi API hoặc service khi người dùng thao tác.
def render_admin_distributed_query(token):
    """Vẽ màn hình/khối giao diện admin truy vấn phân tán và gọi API hoặc service khi người dùng thao tác."""
    page_title("Truy vấn phân tán / Thống kê", "Dữ liệu tổng hợp từ 5 site PostgreSQL.")

    cols = st.columns([0.22, 0.22, 0.22, 0.22, 0.12])
    with cols[0]:
        st.selectbox("Học kỳ", ["Học kỳ 1", "Học kỳ 2", "Học kỳ 3"], index=1)
    with cols[1]:
        st.selectbox("Năm học", ["2024 - 2025", "2025 - 2026"], index=0)
    with cols[2]:
        st.selectbox("Site", ["Tất cả cơ sở", *SITE_LABELS.values()])
    with cols[3]:
        selected = st.selectbox("Loại thống kê", list(QUERIES.keys()), index=0)
    with cols[4]:
        st.write("")
        run = st.button("Truy vấn", use_container_width=True)

    registrations = api_get("/distributed/registration-by-site", token=token)
    classes = api_get("/distributed/classes-by-site", token=token)
    students = api_get("/distributed/students-by-site", token=token)
    cross_site = api_get("/distributed/cross-site-students", token=token)
    fill_rate = api_get("/distributed/fill-rate", token=token)

    metric_cols = st.columns(5)
    with metric_cols[0]:
        metric_card("Tổng sinh viên đăng ký", int(sum_field(registrations, "so_luot_dang_ky")), icon="◌", accent="red", red_value=True)
    with metric_cols[1]:
        metric_card("Tổng lớp học phần", int(sum_field(classes, "so_lop_mo")), icon="▤", accent="blue", red_value=True)
    with metric_cols[2]:
        metric_card("Tổng số lượt đăng ký", int(sum_field(registrations, "so_luot_dang_ky")), icon="▣", accent="green", red_value=True)
    with metric_cols[3]:
        metric_card("Tỷ lệ lấp đầy trung bình", f"{_avg_fill(fill_rate):.2f}%", icon="◒", accent="orange", red_value=True)
    with metric_cols[4]:
        metric_card("Sinh viên đăng ký chéo", records_count(cross_site), icon="⇄", accent="purple", red_value=True)

    left, right = st.columns([0.48, 0.52], gap="medium")
    with left:
        section_title("1. Thống kê số sinh viên đăng ký theo cơ sở")
        chart_rows = _site_names(registrations)
        if isinstance(chart_rows, list) and chart_rows:
            chart_df = pd.DataFrame(chart_rows).rename(columns={"site_label": "Cơ sở", "so_luot_dang_ky": "Số lượt"})
            st.bar_chart(chart_df.set_index("Cơ sở")["Số lượt"], use_container_width=True)
        else:
            st.info("Không có dữ liệu đăng ký theo cơ sở.")

    with right:
        section_title("2. Học phần có nhiều sinh viên đăng ký nhất")
        top_courses = api_get("/distributed/top-courses", token=token)
        html_table(
            top_courses,
            [
                ("id_subject", "Mã học phần"),
                ("name_subject", "Tên học phần"),
                ("so_luot", "Tổng SV đăng ký"),
            ],
            limit=5,
        )

    lower_left, lower_mid, lower_right = st.columns([0.34, 0.24, 0.42], gap="medium")
    with lower_left:
        section_title("3. Danh sách sinh viên đăng ký chéo cơ sở")
        html_table(
            cross_site,
            [
                ("id_student", "MSSV"),
                ("student_headquarter", "Cơ sở gốc"),
                ("class_headquarter", "Đăng ký tại"),
                ("id_class", "Mã lớp"),
                ("status", "Trạng thái"),
            ],
            limit=5,
            status_columns={"status"},
        )
    with lower_mid:
        section_title("4. Tỷ lệ lấp đầy lớp học phần")
        metric_card("Trung bình", f"{_avg_fill(fill_rate):.2f}%", icon="◒", accent="orange", red_value=True)
    with lower_right:
        section_title("5. Thống kê số lớp mở theo cơ sở")
        html_table(
            _site_names(classes),
            [
                ("site_label", "Cơ sở"),
                ("so_lop_mo", "Tổng lớp mở"),
            ],
            limit=None,
        )

    if run:
        st.divider()
        section_title(f"Kết quả truy vấn: {selected}")
        dataframe(api_get(QUERIES[selected], token=token), height=360)
