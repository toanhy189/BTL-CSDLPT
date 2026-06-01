"""Teacher weekly schedule page."""

import pandas as pd
import streamlit as st

from api_client import api_get
from styles import page_title, schedule_grid


def _rows(data):
    return data if isinstance(data, list) else []


def _week_label(week_number, rows):
    dates = []
    for row in rows:
        if row.get("week_number") != week_number:
            continue
        parsed = pd.to_datetime(row.get("study_date"), errors="coerce")
        if not pd.isna(parsed):
            dates.append(parsed)
    if not dates:
        return f"Tuần {week_number}"
    start = min(dates).strftime("%d/%m/%Y")
    end = max(dates).strftime("%d/%m/%Y")
    return f"Tuần {week_number} [từ ngày {start} đến ngày {end}]"


def render_teacher_schedule(token):
    page_title("Lịch dạy", "Thời khóa biểu giảng dạy theo đúng một học kỳ, năm học và tuần.")

    cols = st.columns([0.24, 0.24, 0.28, 0.24])
    with cols[0]:
        semester = st.selectbox("Học kỳ", [1, 2, 3], index=1, format_func=lambda value: f"Học kỳ {value}")
    with cols[1]:
        school_year = st.selectbox("Năm học", [2024, 2025, 2026], index=2, format_func=str)

    base_params = {"semester": semester, "school_year": school_year}
    all_rows = _rows(api_get("/teacher/schedule", token=token, params=base_params))
    weeks = sorted({row.get("week_number") for row in all_rows if row.get("week_number") is not None})

    with cols[2]:
        if weeks:
            week_number = st.selectbox("Tuần", weeks, format_func=lambda value: _week_label(value, all_rows))
        else:
            week_number = None
            st.selectbox("Tuần", ["Không có dữ liệu"], disabled=True)
    with cols[3]:
        st.write("")
        if st.button("Tải lại", use_container_width=True):
            st.rerun()

    if week_number is None:
        st.info("Chưa có lịch dạy cho học kỳ và năm học đang chọn.")
        return

    rows = _rows(api_get("/teacher/schedule", token=token, params={**base_params, "week_number": week_number}))
    schedule_grid(rows, _week_label(week_number, rows))
