"""Trang Streamlit cho nghiệp vụ trang tổng quan của quản trị viên, hiển thị dữ liệu và gửi thao tác của người dùng."""

import pandas as pd
import streamlit as st

from api_client import api_get
from styles import SITE_LABELS, html_table, metric_card, page_title, records_count, section_title, sum_field


# Hàm hỗ trợ chuẩn hóa/lọc/chuẩn bị dữ liệu with site names trước khi hiển thị hoặc xử lý.
def _with_site_names(rows):
    """Hàm hỗ trợ chuẩn hóa/lọc/chuẩn bị dữ liệu with site names trước khi hiển thị hoặc xử lý."""
    if not isinstance(rows, list):
        return rows
    result = []
    for row in rows:
        item = dict(row)
        code = item.get("site_code") or item.get("id_headquarter")
        item["site_name"] = SITE_LABELS.get(code, code)
        result.append(item)
    return result


# Vẽ màn hình/khối giao diện admin tổng quan và gọi API hoặc service khi người dùng thao tác.
def render_admin_dashboard(token):
    """Vẽ màn hình/khối giao diện admin tổng quan và gọi API hoặc service khi người dùng thao tác."""
    page_title("Tổng quan hệ thống", "Theo dõi tình hình hoạt động và các chỉ số tổng hợp của hệ thống.")

    top_left, top_right = st.columns([1, 0.28])
    with top_right:
        if st.button("Làm mới", use_container_width=True):
            st.rerun()

    data = api_get("/admin/dashboard", token=token)
    if data.get("_error"):
        st.error(data["message"])
        return

    site_status = api_get("/admin/sites/status", token=token)
    students_by_site = api_get("/distributed/students-by-site", token=token)
    fill_rate = api_get("/distributed/fill-rate", token=token)

    avg_fill = 0
    fill_rows = fill_rate if isinstance(fill_rate, list) else []
    if fill_rows:
        avg_fill = sum(float(row.get("ty_le_lap_day") or 0) for row in fill_rows) / len(fill_rows)

    cols = st.columns(5)
    metrics = [
        ("Số cơ sở", data.get("sites", 0), "▥", "red", "100% hoạt động"),
        ("Tổng sinh viên", data.get("students", 0), "◌", "blue", "Tổng hợp 5 site"),
        ("Tổng lớp học phần", data.get("class_sections", 0), "▤", "green", "Đang mở"),
        ("Tổng lượt đăng ký", data.get("registrations", 0), "▣", "purple", "Toàn hệ thống"),
        ("Tỷ lệ lấp đầy TB", f"{avg_fill:.2f}%", "◒", "orange", "Theo lớp học phần"),
    ]
    for col, (label, value, icon, accent, note) in zip(cols, metrics):
        with col:
            metric_card(label, value, icon=icon, accent=accent, note=note, red_value=label == "Tỷ lệ lấp đầy TB")

    left, right = st.columns([0.48, 0.52], gap="medium")
    with left:
        section_title("Trạng thái kết nối các cơ sở")
        html_table(
            _with_site_names(site_status),
            [
                ("site_code", "#"),
                ("site_name", "Cơ sở"),
                ("message", "Địa chỉ kết nối"),
                ("status", "Trạng thái"),
            ],
            limit=None,
            status_columns={"status"},
        )
        if isinstance(site_status, list) and all(row.get("status") == "OK" for row in site_status):
            st.success("Tất cả cơ sở hoạt động bình thường")

    with right:
        section_title("Số sinh viên theo cơ sở")
        chart_rows = _with_site_names(students_by_site)
        if isinstance(chart_rows, list) and chart_rows:
            chart_df = pd.DataFrame(chart_rows)
            chart_df = chart_df.rename(columns={"site_name": "Cơ sở", "so_sinh_vien": "Số sinh viên"})
            st.bar_chart(chart_df.set_index("Cơ sở")["Số sinh viên"], use_container_width=True)
        else:
            st.info("Không có dữ liệu thống kê sinh viên.")

    section_title("Hoạt động gần đây")
    st.markdown(
        f"""
        <div class="ui-table-wrap">
            <table class="ui-table">
                <thead>
                    <tr><th>Nội dung</th><th>Loại</th><th>Trạng thái</th></tr>
                </thead>
                <tbody>
                    <tr><td>Đồng bộ dữ liệu từ {records_count(students_by_site)} cơ sở</td><td>Đồng bộ</td><td><span class="status-badge status-ok">Hoàn tất</span></td></tr>
                    <tr><td>Tổng hợp {int(sum_field(students_by_site, "so_sinh_vien"))} sinh viên toàn hệ thống</td><td>Báo cáo</td><td><span class="status-badge status-ok">Hoàn tất</span></td></tr>
                    <tr><td>Kiểm tra trạng thái kết nối cơ sở đào tạo</td><td>Giám sát</td><td><span class="status-badge status-ok">Hoàn tất</span></td></tr>
                </tbody>
            </table>
        </div>
        """,
        unsafe_allow_html=True,
    )
