"""Trang tổng quan dành cho quản trị viên."""

import pandas as pd
import streamlit as st

from api_client import api_get, api_post
from styles import SITE_LABELS, html_table, metric_card, page_title, section_title


def _with_site_names(rows):
    rows = _rows(rows)
    if not isinstance(rows, list):
        return rows
    result = []
    for row in rows:
        item = dict(row)
        code = item.get("site_code") or item.get("id_headquarter")
        item["site_name"] = SITE_LABELS.get(code, code)
        result.append(item)
    return result


def _rows(response):
    if isinstance(response, dict) and isinstance(response.get("data"), list):
        return response["data"]
    return response


def _show_site_warning(response):
    if not isinstance(response, dict):
        return
    failed_sites = response.get("failed_sites") or []
    if failed_sites:
        labels = ", ".join(SITE_LABELS.get(site, site) for site in failed_sites)
        st.warning(response.get("warning") or f"Kết quả chưa bao gồm site: {labels}")


def render_admin_dashboard(token):
    page_title("Tổng quan hệ thống", "Theo dõi trạng thái các cơ sở và số liệu đăng ký học phần.")

    data = api_get("/admin/dashboard", token=token)
    if data.get("_error"):
        st.error(data["message"])
        return

    site_status = api_get("/admin/sites/status", token=token)
    registration_status = api_get("/admin/registration-status", token=token)
    students_by_site = api_get("/distributed/students-by-site", token=token)
    fill_rate = api_get("/distributed/fill-rate", token=token)
    _show_site_warning(students_by_site)
    _show_site_warning(fill_rate)

    registration_open = True
    if isinstance(registration_status, dict) and not registration_status.get("_error"):
        registration_open = bool(registration_status.get("registration_open", True))

    top_cols = st.columns([0.72, 0.14, 0.14])
    with top_cols[0]:
        st.success("Đăng ký học phần đang mở") if registration_open else st.warning("Đăng ký học phần đang đóng")
    with top_cols[1]:
        if st.button("Đóng đăng ký" if registration_open else "Mở đăng ký", use_container_width=True):
            result = api_post(
                "/admin/registration-status",
                token=token,
                json={"registration_open": not registration_open},
            )
            if result.get("_error"):
                st.error(result["message"])
            else:
                st.rerun()
    with top_cols[2]:
        if st.button("Tải lại", use_container_width=True):
            st.rerun()

    avg_fill = 0
    fill_rows = _rows(fill_rate)
    if isinstance(fill_rows, list) and fill_rows:
        avg_fill = sum(float(row.get("ty_le_lap_day") or 0) for row in fill_rows) / len(fill_rows)

    metric_cols = st.columns(5)
    metrics = [
        ("Số cơ sở", data.get("sites", 0), "Toàn hệ thống"),
        ("Tổng sinh viên", data.get("students", 0), "Toàn trường"),
        ("Tổng lớp học phần", data.get("class_sections", 0), "Các cơ sở mở lớp"),
        ("Tổng lượt đăng ký", data.get("registrations", 0), "Trạng thái còn hiệu lực"),
        ("Lấp đầy trung bình", f"{avg_fill:.2f}%", "Theo lớp học phần"),
    ]
    for col, (label, value, note) in zip(metric_cols, metrics):
        with col:
            metric_card(label, value, note=note, red_value=label == "Số cơ sở")

    left, right = st.columns([0.48, 0.52], gap="medium")
    with left:
        section_title("Trạng thái kết nối các cơ sở")
        html_table(
            _with_site_names(site_status),
            [
                ("site_code", "Mã"),
                ("site_name", "Cơ sở"),
                ("message", "Thông tin kết nối"),
                ("status", "Trạng thái"),
            ],
            limit=None,
            status_columns={"status"},
        )

    with right:
        section_title("Số sinh viên theo cơ sở")
        chart_rows = _with_site_names(students_by_site)
        if isinstance(chart_rows, list) and chart_rows:
            chart_df = pd.DataFrame(chart_rows).rename(columns={"site_name": "Cơ sở", "so_sinh_vien": "Số sinh viên"})
            st.bar_chart(chart_df.set_index("Cơ sở")["Số sinh viên"], use_container_width=True)
        else:
            st.info("Không có dữ liệu thống kê sinh viên.")
