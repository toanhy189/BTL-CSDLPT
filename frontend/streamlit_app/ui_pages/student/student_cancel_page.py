"""Student cancel registration page."""

import streamlit as st

from api_client import api_get, api_post
from styles import SITE_LABELS, html_table, page_title, section_title


def _active_regs(rows):
    if not isinstance(rows, list):
        return []
    return [row for row in rows if row.get("status") == "DA_DANG_KY"]


def render_student_cancel(token, user):
    page_title("Hủy đăng ký", "Hủy một lớp học phần đang có hiệu lực.")

    registrations = api_get("/student/registrations", token=token)
    active_regs = _active_regs(registrations)

    section_title("Danh sách học phần hiện tại")
    html_table(
        registrations,
        [
            ("id_class", "Mã lớp"),
            ("name_subject", "Tên học phần"),
            ("class_headquarter", "Cơ sở mở lớp"),
            ("registration_date", "Ngày đăng ký"),
            ("status", "Trạng thái"),
        ],
        status_columns={"status"},
        limit=12,
    )

    if not active_regs:
        st.info("Không có lớp đang đăng ký để hủy.")
        return

    c1, c2 = st.columns([0.72, 0.28])
    with c1:
        selected = st.selectbox(
            "Chọn lớp cần hủy",
            active_regs,
            format_func=lambda row: f"{row.get('id_class')} - {row.get('name_subject')} - {SITE_LABELS.get(row.get('class_headquarter'), row.get('class_headquarter'))}",
        )
    with c2:
        st.write("")
        if st.button("Hủy đăng ký", use_container_width=True):
            res = api_post(
                "/student/cancel",
                token=token,
                json={
                    "student_id": user.get("ref_id"),
                    "class_site_code": selected.get("site_code") or selected.get("class_headquarter"),
                    "class_id": selected.get("id_class"),
                },
            )
            if res.get("success"):
                st.success(res["message"])
                st.rerun()
            else:
                st.error(res.get("message", res.get("detail", "Hủy đăng ký thất bại")))
