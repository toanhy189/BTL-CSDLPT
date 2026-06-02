"""Trang sinh viên đăng ký học phần."""

import streamlit as st

from api_client import api_get, api_post
from styles import SITE_LABELS, html_table, metric_card, page_title, records_count, section_title


SITE_CODES = ["HL", "NT", "HD", "CG", "HCM"]


def _int_value(value, default=0):
    try:
        return int(value or default)
    except (TypeError, ValueError):
        return default


def _decorate_classes(rows):
    if not isinstance(rows, list):
        return []
    decorated = []
    for row in rows:
        item = dict(row)
        site = item.get("id_headquarter")
        current = _int_value(item.get("number_of_student"))
        maximum = _int_value(item.get("max_student"))
        remaining = max(maximum - current, 0)
        item["site_name"] = SITE_LABELS.get(site, site)
        item["remaining"] = remaining
        item["capacity"] = f"{current}/{maximum}"
        item["class_status"] = "Hết chỗ" if remaining <= 0 else "Còn chỗ"
        item["rooms"] = item.get("id_rooms") or "Chưa có lịch"
        item["schedule_text"] = item.get("schedule_summary") or "Chưa có lịch"
        search_text = item.get("name_subject") or item.get("id_subject") or ""
        item["search_text"] = f"{item.get('id')} {item.get('id_subject')} {search_text}".lower()
        decorated.append(item)
    return decorated


def _filter_rows(rows, semester, school_year, keyword, only_available):
    result = []
    needle = keyword.strip().lower()
    for row in rows:
        if _int_value(row.get("semester")) != semester:
            continue
        if _int_value(row.get("school_year")) != school_year:
            continue
        if only_available and _int_value(row.get("remaining")) <= 0:
            continue
        if needle and needle not in row.get("search_text", ""):
            continue
        result.append(row)
    return result


def _active_regs(rows):
    if not isinstance(rows, list):
        return []
    return [row for row in rows if row.get("status") == "DA_DANG_KY"]


def _registered_class_ids(rows):
    return {row.get("id_class") for row in _active_regs(rows)}


def _registered_subjects(rows):
    subjects = {}
    for row in _active_regs(rows):
        subject = row.get("id_subject") or row.get("name_subject")
        if subject:
            subjects[subject] = row.get("id_class")
    return subjects


def _action_state(row, registered_ids, registered_subjects):
    if row.get("id") in registered_ids:
        return "Đã đăng ký", True
    if _int_value(row.get("remaining")) <= 0:
        return "Hết chỗ", True
    subject_key = row.get("id_subject") or row.get("name_subject")
    if subject_key and subject_key in registered_subjects:
        return "Đổi lớp", False
    return "Đăng ký", False


def _render_class_rows(rows, registered, token, user, site):
    registered_ids = _registered_class_ids(registered)
    registered_subjects = _registered_subjects(registered)

    if not rows:
        st.info("Không có lớp học phần phù hợp với bộ lọc.")
        return

    header = st.columns([0.1, 0.25, 0.14, 0.08, 0.28, 0.08, 0.07])
    labels = ["Mã lớp", "Học phần", "Giảng viên", "Sĩ số", "Thời khóa biểu", "Trạng thái", ""]
    for col, label in zip(header, labels):
        col.markdown(f"**{label}**")

    with st.container(height=520, border=True):
        for row in rows:
            cols = st.columns([0.1, 0.25, 0.14, 0.08, 0.28, 0.08, 0.07])
            cols[0].write(row.get("id"))
            cols[1].write(row.get("name_subject"))
            cols[2].write(row.get("name_teacher"))
            cols[3].write(row.get("capacity"))
            schedule_text = str(row.get("schedule_text") or "Chưa có lịch").replace("\n", "  \n")
            cols[4].markdown(schedule_text)
            cols[5].write(row.get("class_status"))

            label, disabled = _action_state(row, registered_ids, registered_subjects)
            if cols[6].button(label, key=f"register_{site}_{row.get('id')}", disabled=disabled, use_container_width=True):
                res = api_post(
                    "/student/register",
                    token=token,
                    json={
                        "student_id": user.get("ref_id"),
                        "student_headquarter": user.get("id_headquarter"),
                        "class_site_code": site,
                        "class_id": row.get("id"),
                    },
                )
                if res.get("success"):
                    st.success(res["message"])
                    st.rerun()
                else:
                    st.error(res.get("message", res.get("detail", "Đăng ký thất bại")))
            st.divider()


def render_student_registration(token, user):
    page_title(
        "Đăng ký học phần",
        "Chọn lớp học phần đang mở để đăng ký. Nếu đã học cùng học phần, hệ thống tự chuyển sang đổi lớp.",
    )

    cols = st.columns([0.14, 0.14, 0.2, 0.16, 0.28, 0.08])
    with cols[0]:
        semester = st.selectbox("Học kỳ", [1, 2, 3], index=1, format_func=lambda value: f"Học kỳ {value}")
    with cols[1]:
        school_year = st.selectbox("Năm học", [2024, 2025, 2026], index=2, format_func=str)
    with cols[2]:
        site = st.selectbox("Cơ sở mở lớp", SITE_CODES, format_func=lambda code: SITE_LABELS.get(code, code))
    with cols[3]:
        only_available = st.checkbox("Chỉ lớp còn chỗ", value=False)
    with cols[4]:
        keyword = st.text_input("Tìm học phần", placeholder="Mã lớp, mã học phần hoặc tên học phần")
    with cols[5]:
        st.write("")
        if st.button("Tải lại", use_container_width=True):
            st.rerun()

    classes = api_get("/student/open-classes", token=token, params={"site_code": site})
    if isinstance(classes, dict) and classes.get("_error"):
        st.error(classes.get("message"))
        return
    registered = api_get("/student/registrations", token=token)
    active_regs = _active_regs(registered)

    decorated = _decorate_classes(classes)
    filtered = _filter_rows(decorated, semester, school_year, keyword, only_available)

    metric_cols = st.columns(4)
    with metric_cols[0]:
        metric_card("Lớp đang hiển thị", records_count(filtered), note=SITE_LABELS.get(site, site), red_value=True)
    with metric_cols[1]:
        metric_card("Đã đăng ký", len(active_regs), note="Đang có hiệu lực")
    with metric_cols[2]:
        metric_card("Cơ sở sinh viên", SITE_LABELS.get(user.get("id_headquarter"), user.get("id_headquarter")), note="Nơi quản lý hồ sơ")
    with metric_cols[3]:
        metric_card("Trạng thái", "Đang mở", note="Theo lịch đăng ký")

    section_title("Danh sách lớp học phần mở cho đăng ký")
    _render_class_rows(filtered, registered, token, user, site)

    section_title("Học phần đã đăng ký")
    html_table(
        active_regs,
        [
            ("id_class", "Mã lớp"),
            ("name_subject", "Học phần"),
            ("class_headquarter", "Cơ sở mở lớp"),
            ("registration_date", "Ngày đăng ký"),
            ("status", "Trạng thái"),
        ],
        limit=None,
        status_columns={"status"},
    )
