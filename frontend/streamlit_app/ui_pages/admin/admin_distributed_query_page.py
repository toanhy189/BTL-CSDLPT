"""Trang quản trị truy vấn phân tán."""

import pandas as pd
import streamlit as st

from api_client import api_get
from styles import SITE_LABELS, dataframe, html_table, metric_card, page_title, records_count, section_title, sum_field


QUERIES = {
    "Đăng ký theo cơ sở": {
        "path": "/distributed/registration-by-site",
        "desc": "Đọc LopHocPhan và DangKy tại 5 site, tổng hợp số lượt đăng ký theo cơ sở mở lớp.",
    },
    "Học phần đăng ký nhiều nhất": {
        "path": "/distributed/top-courses",
        "desc": "Đọc HocPhan, LopHocPhan, DangKy tại 5 site, sau đó nhóm theo học phần.",
    },
    "Sinh viên đăng ký chéo cơ sở": {
        "path": "/distributed/cross-site-students",
        "desc": "Tìm đăng ký có cơ sở sinh viên khác cơ sở mở lớp học phần.",
    },
    "Tỷ lệ lấp đầy lớp học phần": {
        "path": "/distributed/fill-rate",
        "desc": "Tính number_of_student / max_student cho từng lớp trên toàn hệ thống.",
    },
    "Số lớp mở theo cơ sở": {
        "path": "/distributed/classes-by-site",
        "desc": "Đếm số LopHocPhan theo cơ sở mở lớp trên các site.",
    },
    "Số sinh viên theo cơ sở": {
        "path": "/distributed/students-by-site",
        "desc": "Đếm SinhVien theo cơ sở quản lý hồ sơ trên các site.",
    },
}


def _site_names(rows):
    rows = _rows(rows)
    if not isinstance(rows, list):
        return rows
    result = []
    for row in rows:
        item = dict(row)
        code = item.get("id_headquarter") or item.get("site_code")
        item["site_label"] = SITE_LABELS.get(code, item.get("site_name", code))
        result.append(item)
    return result


def _avg_fill(rows):
    rows = _rows(rows)
    if not isinstance(rows, list) or not rows:
        return 0
    return sum(float(row.get("ty_le_lap_day") or 0) for row in rows) / len(rows)


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


def render_admin_distributed_query(token):
    page_title("Truy vấn phân tán", "Các báo cáo tổng hợp dữ liệu từ nhiều cơ sở đào tạo.")

    registrations = api_get("/distributed/registration-by-site", token=token)
    classes = api_get("/distributed/classes-by-site", token=token)
    students = api_get("/distributed/students-by-site", token=token)
    cross_site = api_get("/distributed/cross-site-students", token=token)
    fill_rate = api_get("/distributed/fill-rate", token=token)
    for response in [registrations, classes, students, cross_site, fill_rate]:
        _show_site_warning(response)

    metric_cols = st.columns(5)
    with metric_cols[0]:
        metric_card("Số sinh viên", int(sum_field(students, "so_sinh_vien")), red_value=True)
    with metric_cols[1]:
        metric_card("Số lớp mở", int(sum_field(classes, "so_lop_mo")))
    with metric_cols[2]:
        metric_card("Lượt đăng ký", int(sum_field(registrations, "so_luot_dang_ky")))
    with metric_cols[3]:
        metric_card("Đăng ký chéo", records_count(cross_site))
    with metric_cols[4]:
        metric_card("Lấp đầy TB", f"{_avg_fill(fill_rate):.2f}%")

    selected = st.selectbox("Chọn truy vấn phân tán", list(QUERIES.keys()))
    st.info(QUERIES[selected]["desc"])
    result = api_get(QUERIES[selected]["path"], token=token)
    section_title(f"Kết quả: {selected}")
    _show_site_warning(result)
    dataframe(result, height=360)

    left, right = st.columns([0.48, 0.52], gap="medium")
    with left:
        section_title("Đăng ký theo cơ sở")
        rows = _site_names(registrations)
        if isinstance(rows, list) and rows:
            chart_df = pd.DataFrame(rows).rename(columns={"site_label": "Cơ sở", "so_luot_dang_ky": "Số lượt"})
            st.bar_chart(chart_df.set_index("Cơ sở")["Số lượt"], use_container_width=True)
        else:
            st.info("Không có dữ liệu đăng ký.")
    with right:
        section_title("Top học phần")
        top_courses = api_get("/distributed/top-courses", token=token)
        _show_site_warning(top_courses)
        html_table(
            top_courses,
            [
                ("id_subject", "Mã học phần"),
                ("name_subject", "Tên học phần"),
                ("so_luot", "Tổng lượt"),
            ],
            limit=8,
        )

    section_title("Đăng ký chéo cơ sở")
    html_table(
        cross_site,
        [
            ("id_student", "MSSV"),
            ("student_headquarter", "Cơ sở sinh viên"),
            ("class_headquarter", "Cơ sở mở lớp"),
            ("id_class", "Mã lớp"),
            ("registration_date", "Ngày đăng ký"),
            ("status", "Trạng thái"),
        ],
        limit=10,
        status_columns={"status"},
    )
