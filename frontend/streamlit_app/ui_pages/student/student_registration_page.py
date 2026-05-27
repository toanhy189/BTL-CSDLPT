"""Trang Streamlit cho nghiệp vụ trang đăng ký học phần của sinh viên, hiển thị dữ liệu và gửi thao tác của người dùng."""

import streamlit as st

from api_client import api_get, api_post
from styles import SITE_LABELS, html_table, metric_card, page_title, records_count, section_title


SITE_CODES = ["HL", "NT", "HD", "CG", "HCM"]


# Bổ sung nhãn hiển thị, cơ sở, sĩ số còn lại và thông tin lịch cho danh sách lớp mở.
def _decorate_classes(rows):
    """Bổ sung nhãn hiển thị, cơ sở, sĩ số còn lại và thông tin lịch cho danh sách lớp mở."""
    if not isinstance(rows, list):
        return []
    decorated = []
    for row in rows:
        item = dict(row)
        site = item.get("id_headquarter")
        item["site_name"] = SITE_LABELS.get(site, site)
        item["credits"] = item.get("number_of_credit") or item.get("credits") or ""
        current = int(item.get("number_of_student") or 0)
        maximum = int(item.get("max_student") or 0)
        item["remaining"] = max(maximum - current, 0)
        item["capacity"] = f"{current} / {maximum}"
        item["schedule"] = item.get("id_rooms") or "Đang cập nhật"
        return_id = item.get("id") or item.get("id_class")
        item["display"] = f"{return_id} - {item.get('name_subject', '')}"
        decorated.append(item)
    return decorated


# Lọc danh sách lớp học phần theo từ khóa người dùng nhập.
def _filter_rows(rows, keyword):
    """Lọc danh sách lớp học phần theo từ khóa người dùng nhập."""
    if not keyword:
        return rows
    needle = keyword.strip().lower()
    return [
        row
        for row in rows
        if needle in str(row.get("id", "")).lower()
        or needle in str(row.get("id_class", "")).lower()
        or needle in str(row.get("name_subject", "")).lower()
    ]


# Vẽ màn hình/khối giao diện sinh viên registration và gọi API hoặc service khi người dùng thao tác.
def render_student_registration(token, user):
    """Vẽ màn hình/khối giao diện sinh viên registration và gọi API hoặc service khi người dùng thao tác."""
    page_title("Đăng ký học phần", "Chọn lớp học phần đang mở để đăng ký.")

    cols = st.columns([0.2, 0.2, 0.24, 0.28, 0.08])
    with cols[0]:
        semester = st.selectbox("Học kỳ", ["Học kỳ 1", "Học kỳ 2", "Học kỳ 3"], index=1)
    with cols[1]:
        school_year = st.selectbox("Năm học", ["2024 - 2025", "2025 - 2026"], index=0)
    with cols[2]:
        site = st.selectbox("Cơ sở mở lớp", SITE_CODES, format_func=lambda code: SITE_LABELS.get(code, code))
    with cols[3]:
        keyword = st.text_input("Tìm kiếm học phần", placeholder="Nhập mã hoặc tên học phần...")
    with cols[4]:
        st.write("")
        if st.button("Làm mới", use_container_width=True):
            st.rerun()

    classes = api_get("/student/open-classes", token=token, params={"site_code": site})
    if isinstance(classes, dict) and classes.get("_error"):
        st.error(classes.get("message"))
        return

    decorated = _filter_rows(_decorate_classes(classes), keyword)
    registered = api_get("/student/registrations", token=token)

    section_title(
        f"1. Danh sách học phần mở lớp ({records_count(decorated)})",
        f"{semester} · {school_year} · {SITE_LABELS.get(site, site)}",
    )
    html_table(
        decorated,
        [
            ("id", "Mã lớp"),
            ("name_subject", "Tên học phần"),
            ("id_subject", "Mã HP"),
            ("credits", "Số TC"),
            ("site_name", "Cơ sở"),
            ("capacity", "Sĩ số"),
            ("remaining", "Còn lại"),
            ("__progress__", "Tỷ lệ"),
            ("schedule", "Phòng học"),
        ],
        limit=8,
        progress=("number_of_student", "max_student"),
    )

    if decorated:
        c1, c2 = st.columns([0.72, 0.28])
        with c1:
            selected = st.selectbox(
                "Chọn lớp để đăng ký",
                decorated,
                format_func=lambda row: row.get("display", row.get("id", "")),
            )
        with c2:
            st.write("")
            if st.button("Đăng ký", use_container_width=True):
                res = api_post(
                    "/student/register",
                    token=token,
                    json={
                        "student_id": user.get("ref_id"),
                        "student_headquarter": user.get("id_headquarter"),
                        "class_site_code": site,
                        "class_id": selected.get("id") or selected.get("id_class"),
                    },
                )
                if res.get("success"):
                    st.success(res["message"])
                else:
                    st.error(res.get("message", res.get("detail", "Đăng ký thất bại")))

    st.divider()
    reg_cols = st.columns(3)
    with reg_cols[0]:
        metric_card("Học phần đã đăng ký", records_count(registered), icon="▤", accent="green")
    with reg_cols[1]:
        metric_card("Cơ sở đang chọn", SITE_LABELS.get(site, site), icon="▥", accent="blue")
    with reg_cols[2]:
        metric_card("Trạng thái", "Đang mở", icon="◉", accent="red", red_value=True)

    section_title(f"2. Danh sách học phần đã đăng ký ({records_count(registered)})")
    html_table(
        registered,
        [
            ("id_class", "Mã lớp"),
            ("name_subject", "Tên học phần"),
            ("class_headquarter", "Cơ sở mở lớp"),
            ("registration_date", "Thời gian đăng ký"),
            ("status", "Trạng thái"),
            ("site_name", "Site xử lý"),
        ],
        limit=8,
        status_columns={"status"},
    )
