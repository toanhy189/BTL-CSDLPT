"""Shared Streamlit UI helpers for the course registration portal."""

from __future__ import annotations

import html
from collections.abc import Iterable
from typing import Any

import pandas as pd
import streamlit as st


ROLE_LABELS = {
    "ADMIN": "Quản trị viên",
    "GIANG_VIEN": "Giảng viên",
    "SINH_VIEN": "Sinh viên",
}

ROLE_PORTALS = {
    "ADMIN": "Cổng quản trị đào tạo",
    "GIANG_VIEN": "Cổng giảng viên",
    "SINH_VIEN": "Cổng sinh viên",
}

SITE_LABELS = {
    "HL": "Cơ sở Hòa Lạc",
    "NT": "Cơ sở Ngọc Trúc",
    "HD": "Cơ sở Hà Đông",
    "CG": "Cơ sở Cầu Giấy",
    "HCM": "Cơ sở TP.HCM",
}


def _escape(value: Any) -> str:
    if value is None:
        return ""
    return html.escape(str(value))


def _number(value: Any) -> str:
    try:
        if isinstance(value, str) and not value.strip():
            return "0"
        number = float(value)
    except (TypeError, ValueError):
        return _escape(value)
    if number.is_integer():
        return f"{int(number):,}".replace(",", ".")
    return f"{number:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _records(data: Any) -> list[dict[str, Any]]:
    if data is None or (isinstance(data, dict) and data.get("_error")):
        return []
    if isinstance(data, pd.DataFrame):
        return data.astype(object).where(pd.notnull(data), None).to_dict(orient="records")
    if isinstance(data, dict):
        return [data]
    if isinstance(data, Iterable) and not isinstance(data, (str, bytes)):
        return [row for row in data if isinstance(row, dict)]
    return []


def load_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --portal-red: #b5121b;
            --portal-red-dark: #8f0f17;
            --portal-red-soft: #f9d7da;
            --portal-border: #e5b5b9;
            --portal-line: #e5e7eb;
            --portal-text: #111827;
            --portal-muted: #667085;
            --portal-bg: #ffffff;
            --portal-blue: #dbeafe;
            --portal-green: #dcfce7;
            --portal-warn: #fff7ed;
        }

        #MainMenu, footer, header { visibility: hidden; }

        .stApp {
            background: #fff;
            color: var(--portal-text);
            font-family: Arial, "Segoe UI", sans-serif;
        }

        .block-container {
            max-width: 1680px;
            padding: 0 1rem 2rem 1rem;
        }

        h1, h2, h3, h4, h5, h6, p, label, span, div {
            letter-spacing: 0;
        }

        [data-testid="stSidebar"] {
            background: #ffffff;
            border-right: 1px solid var(--portal-border);
        }

        [data-testid="stSidebar"] > div:first-child {
            padding: .65rem .75rem 1rem .75rem;
        }

        .sidebar-brand {
            padding: 8px 4px 14px 4px;
            border-bottom: 1px solid var(--portal-border);
            margin-bottom: 8px;
        }

        .sidebar-title {
            color: var(--portal-red);
            font-weight: 800;
            font-size: 13px;
            line-height: 1.25;
        }

        .sidebar-subtitle {
            color: #555;
            font-size: 12px;
            margin-top: 3px;
        }

        .sidebar-group {
            color: var(--portal-red);
            font-size: 12px;
            font-weight: 700;
            padding: 6px 4px;
        }

        [data-testid="stSidebar"] .stRadio > label {
            display: none;
        }

        [data-testid="stSidebar"] div[role="radiogroup"] {
            gap: 0;
        }

        [data-testid="stSidebar"] div[role="radiogroup"] label {
            min-height: 38px;
            padding: 8px 8px;
            border-radius: 0;
            color: #111;
            font-weight: 500;
            border-bottom: 1px solid var(--portal-border);
        }

        [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
            background: var(--portal-red-soft);
            color: var(--portal-red-dark);
            font-weight: 700;
        }

        [data-testid="stSidebar"] .stButton button {
            width: 100%;
        }

        .support-box {
            margin-top: 18px;
            padding: 10px;
            border-top: 1px solid var(--portal-border);
            color: #555;
            font-size: 12px;
        }

        .support-title {
            color: var(--portal-red);
            font-weight: 700;
            margin-bottom: 4px;
        }

        .portal-header {
            min-height: 50px;
            background: var(--portal-red);
            color: white;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 7px 12px;
            margin: 0 -1rem 14px -1rem;
        }

        .brand-title {
            font-size: 16px;
            font-weight: 800;
            line-height: 1.15;
        }

        .brand-subtitle {
            font-size: 12px;
            opacity: .95;
            margin-top: 2px;
        }

        .top-actions,
        .user-pill {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .bell {
            width: 28px;
            height: 28px;
            border-radius: 99px;
            border: 1px solid rgba(255,255,255,.55);
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
        }

        .avatar {
            width: 34px;
            height: 34px;
            border-radius: 99px;
            background: #ffffff;
            color: var(--portal-red);
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
        }

        .user-name {
            font-size: 13px;
            font-weight: 700;
            color: white;
        }

        .user-role {
            font-size: 11px;
            color: rgba(255,255,255,.9);
        }

        .page-title-wrap {
            margin: 10px 0 12px 0;
        }

        .page-title {
            font-size: 22px;
            color: #111;
            font-weight: 800;
        }

        .page-subtitle {
            font-size: 13px;
            color: var(--portal-muted);
            margin-top: 3px;
        }

        .section-head {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            border: 1px solid var(--portal-red);
            border-bottom: 0;
            border-radius: 7px 7px 0 0;
            padding: 9px 12px;
            margin-top: 12px;
            background: #fff;
        }

        .section-title {
            color: #111;
            font-size: 15px;
            font-weight: 800;
        }

        .section-subtitle {
            color: var(--portal-muted);
            font-size: 12px;
            margin-top: 2px;
        }

        .plain-section-title {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            margin: 14px 0 8px 0;
            padding-bottom: 7px;
            border-bottom: 1px solid var(--portal-red);
        }

        .section-right {
            color: var(--portal-muted);
            font-size: 12px;
        }

        div[data-testid="stVerticalBlock"]:has(.card-surface-marker) {
            border: 1px solid var(--portal-red);
            border-radius: 7px;
            padding: 12px 14px;
            background: #fff;
        }

        .metric-card {
            border: 1px solid var(--portal-border);
            border-radius: 7px;
            padding: 12px 13px;
            background: #fff;
            min-height: 86px;
        }

        .metric-label {
            color: #555;
            font-size: 12px;
            font-weight: 700;
        }

        .metric-value {
            color: #111;
            font-size: 22px;
            font-weight: 800;
            margin-top: 4px;
        }

        .metric-value.red { color: var(--portal-red); }
        .metric-note { color: var(--portal-muted); font-size: 12px; margin-top: 5px; }

        div.stButton > button,
        div[data-testid="stFormSubmitButton"] button {
            border-radius: 5px;
            border: 1px solid var(--portal-red);
            background: var(--portal-red);
            color: white;
            font-weight: 700;
            min-height: 36px;
        }

        div.stButton > button:hover,
        div[data-testid="stFormSubmitButton"] button:hover {
            background: var(--portal-red-dark);
            border-color: var(--portal-red-dark);
            color: white;
        }

        .stTextInput input,
        .stNumberInput input,
        .stDateInput input,
        .stTextArea textarea,
        .stSelectbox div[data-baseweb="select"] {
            border-radius: 4px;
            min-height: 35px;
        }

        .ui-table-wrap {
            border: 1px solid var(--portal-red);
            border-radius: 0 0 7px 7px;
            overflow: hidden;
            background: white;
            margin-bottom: 18px;
        }

        .ui-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 12px;
        }

        .ui-table th {
            text-align: left;
            background: #fff;
            color: #111;
            font-weight: 800;
            padding: 8px 10px;
            border-bottom: 1px solid var(--portal-red);
            white-space: nowrap;
        }

        .ui-table td {
            padding: 8px 10px;
            border-bottom: 1px solid #eee;
            color: #111;
            vertical-align: middle;
        }

        .ui-table tr:nth-child(even) td {
            background: #fafafa;
        }

        .status-badge {
            display: inline-flex;
            border-radius: 4px;
            padding: 3px 7px;
            font-size: 11px;
            font-weight: 800;
            border: 1px solid transparent;
            white-space: nowrap;
        }

        .status-ok { color: #166534; background: #dcfce7; border-color: #86efac; }
        .status-warn { color: #92400e; background: #fffbeb; border-color: #fcd34d; }
        .status-error { color: #991b1b; background: #fee2e2; border-color: #fca5a5; }

        .progress-track {
            width: 110px;
            height: 7px;
            background: #e5e7eb;
            overflow: hidden;
        }

        .progress-fill { height: 100%; background: #16a34a; }
        .progress-fill.warn { background: #f59e0b; }
        .progress-fill.danger { background: var(--portal-red); }

        .empty-state {
            border: 1px solid var(--portal-red);
            border-radius: 0 0 7px 7px;
            padding: 18px;
            color: #777;
            text-align: center;
            background: #f3f4f6;
            margin-bottom: 18px;
        }

        .schedule-grid {
            width: 100%;
            border-collapse: collapse;
            table-layout: fixed;
            font-size: 12px;
            border: 1px solid var(--portal-red);
            margin-bottom: 16px;
        }

        .schedule-grid th,
        .schedule-grid td {
            border: 1px solid #d7dde5;
            padding: 0;
            min-height: 58px;
            vertical-align: top;
            background: white;
        }

        .schedule-grid th {
            text-align: center;
            background: #fff;
            font-weight: 800;
            padding: 8px 4px;
        }

        .slot-label {
            width: 70px;
            color: white;
            background: var(--portal-red) !important;
            font-weight: 800;
            text-align: center;
            padding: 8px 4px !important;
        }

        .event-pill {
            min-height: 100%;
            padding: 7px 8px;
            line-height: 1.35;
            border: 1px solid #ef4444;
            background: #cfe3ff;
            color: #111;
            font-weight: 600;
        }

        .event-title { font-weight: 800; }
        .event-sub { font-size: 11px; margin-top: 2px; }

        [data-testid="stDataFrame"] {
            border: 1px solid var(--portal-line);
            border-radius: 6px;
            overflow: hidden;
        }

        .login-page-marker { display: none; }
        .stApp:has(.login-page-marker) [data-testid="stSidebar"] { display: none; }
        .stApp:has(.login-page-marker) .block-container { padding-top: 5rem; max-width: 1120px; }
        .login-title { color: var(--portal-red); font-size: 30px; font-weight: 900; text-transform: uppercase; }
        .login-subtitle { color: #333; font-size: 16px; margin: 8px 0 24px 0; }
        .login-feature { border-left: 3px solid var(--portal-red); padding: 8px 12px; margin: 10px 0; }
        .feature-title { font-weight: 800; }
        .feature-sub { color: #555; font-size: 13px; }
        .login-card-title { color: var(--portal-red); font-size: 22px; font-weight: 900; }
        .login-card-sub { color: #555; margin-bottom: 16px; }
        .login-secondary, .forgot-link, .login-footer-text { color: #555; font-size: 13px; margin-top: 10px; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def login_mode_css() -> None:
    st.markdown('<div class="login-page-marker"></div>', unsafe_allow_html=True)


def role_portal(user: dict[str, Any] | None) -> str:
    if not user:
        return "Cổng quản lý đào tạo"
    return ROLE_PORTALS.get(user.get("role", ""), "Cổng quản lý đào tạo")


def render_header(user: dict[str, Any] | None = None, subtitle: str = "Cổng quản lý đào tạo") -> None:
    name = "Khách"
    role = ""
    initials = "?"
    if user:
        name = user.get("full_name") or user.get("username") or "Người dùng"
        role = ROLE_LABELS.get(user.get("role", ""), user.get("role", ""))
        source = user.get("username") or name
        initials = (source[:2] or "?").upper()

    st.markdown(
        f"""
        <div class="portal-header">
            <div>
                <div class="brand-title">Hệ thống đăng ký học phần nhiều cơ sở</div>
                <div class="brand-subtitle">{_escape(subtitle)}</div>
            </div>
            <div class="top-actions">
                <div class="bell">!</div>
                <div class="user-pill">
                    <div class="avatar">{_escape(initials)}</div>
                    <div>
                        <div class="user-name">{_escape(name)}</div>
                        <div class="user-role">{_escape(role)}</div>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_brand(subtitle: str) -> None:
    st.sidebar.markdown(
        f"""
        <div class="sidebar-brand">
            <div class="sidebar-title">Hệ thống đăng ký học phần nhiều cơ sở</div>
            <div class="sidebar-subtitle">{_escape(subtitle)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_support_box(role: str) -> None:
    title = {
        "ADMIN": "Hỗ trợ quản trị",
        "GIANG_VIEN": "Hỗ trợ giảng viên",
        "SINH_VIEN": "Hỗ trợ sinh viên",
    }.get(role, "Hỗ trợ")
    st.sidebar.markdown(
        f"""
        <div class="support-box">
            <div class="support-title">{_escape(title)}</div>
            <div>Dữ liệu demo nhiều cơ sở</div>
            <div style="margin-top:4px;">Hỗ trợ đồ án CSDL phân tán</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def page_title(title: str, subtitle: str | None = None) -> None:
    subtitle_html = f'<div class="page-subtitle">{_escape(subtitle)}</div>' if subtitle else ""
    st.markdown(
        f"""
        <div class="page-title-wrap">
            <div class="page-title">{_escape(title)}</div>
            {subtitle_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_title(title: str, subtitle: str | None = None, right: str | None = None) -> None:
    if right:
        st.markdown(f"**{title}**  \n{right}")
    else:
        st.markdown(f"**{title}**")
    if subtitle:
        st.caption(subtitle)


def metric_card(
    label: str,
    value: Any,
    icon: str = "",
    accent: str = "red",
    note: str | None = None,
    red_value: bool = False,
) -> None:
    note_html = f'<div class="metric-note">{_escape(note)}</div>' if note else ""
    value_class = " red" if red_value else ""
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{_escape(label)}</div>
            <div class="metric-value{value_class}">{_number(value)}</div>
            {note_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def marker_card() -> None:
    st.markdown('<div class="card-surface-marker"></div>', unsafe_allow_html=True)


def filter_panel(title: str | None = None) -> None:
    if title:
        st.markdown(f'<div class="section-title">{_escape(title)}</div>', unsafe_allow_html=True)


def dataframe(data: Any, height: int = 420, rename: dict[str, str] | None = None, columns: list[str] | None = None) -> None:
    if isinstance(data, dict) and data.get("_error"):
        st.error(data.get("message", "Không thể tải dữ liệu"))
        return
    rows = _records(data)
    if not rows:
        st.markdown('<div class="empty-state">Không có dữ liệu</div>', unsafe_allow_html=True)
        return
    df = pd.DataFrame(rows)
    if columns:
        present = [col for col in columns if col in df.columns]
        if present:
            df = df[present]
    if rename:
        df = df.rename(columns=rename)
    st.dataframe(df, use_container_width=True, hide_index=True, height=height)


def _status_class(value: Any) -> str:
    normalized = str(value or "").upper()
    if normalized in {"OK", "DA_DANG_KY", "ACTIVE", "SUCCESS", "TRUE", "THANH_CONG"}:
        return "status-ok"
    if normalized in {"ERROR", "FAILED", "DA_HUY", "HUY", "FALSE", "THAT_BAI"}:
        return "status-error"
    return "status-warn"


def status_badge(value: Any, label: str | None = None) -> str:
    shown = label or str(value or "Đang xử lý")
    return f'<span class="status-badge {_status_class(value)}">{_escape(shown)}</span>'


def progress_bar(current: Any, maximum: Any) -> str:
    try:
        cur = float(current or 0)
        max_value = float(maximum or 0)
        percent = 0 if max_value <= 0 else max(0, min(100, cur / max_value * 100))
    except (TypeError, ValueError):
        percent = 0
    tone = "danger" if percent >= 95 else "warn" if percent >= 80 else ""
    return f'<div class="progress-track"><div class="progress-fill {tone}" style="width:{percent:.0f}%"></div></div>'


def html_table(
    data: Any,
    columns: list[tuple[str, str]],
    limit: int | None = 10,
    empty: str = "Không có dữ liệu",
    status_columns: set[str] | None = None,
    progress: tuple[str, str] | None = None,
) -> None:
    if isinstance(data, dict) and data.get("_error"):
        st.error(data.get("message", "Không thể tải dữ liệu"))
        return
    rows = _records(data)
    if not rows:
        st.markdown(f'<div class="empty-state">{_escape(empty)}</div>', unsafe_allow_html=True)
        return
    shown_rows = rows[:limit] if limit else rows
    status_columns = status_columns or set()
    header = "".join(f"<th>{_escape(label)}</th>" for _, label in columns)
    body_rows = []
    for row in shown_rows:
        cells = []
        for key, _ in columns:
            if progress and key == "__progress__":
                cells.append(f"<td>{progress_bar(row.get(progress[0]), row.get(progress[1]))}</td>")
            elif key in status_columns:
                label = "Đã đăng ký" if row.get(key) == "DA_DANG_KY" else row.get(key)
                cells.append(f"<td>{status_badge(row.get(key), label)}</td>")
            else:
                cells.append(f"<td>{_escape(row.get(key))}</td>")
        body_rows.append(f"<tr>{''.join(cells)}</tr>")
    st.markdown(
        f"""
        <div class="ui-table-wrap">
            <table class="ui-table">
                <thead><tr>{header}</tr></thead>
                <tbody>{''.join(body_rows)}</tbody>
            </table>
        </div>
        """,
        unsafe_allow_html=True,
    )


def schedule_grid(data: Any, title: str = "Thời khóa biểu") -> None:
    rows = _records(data)
    section_title(title)
    if not rows:
        st.markdown('<div class="empty-state">Chưa có lịch học</div>', unsafe_allow_html=True)
        return

    days = [2, 3, 4, 5, 6, 7, 8]
    day_names = {2: "Thứ 2", 3: "Thứ 3", 4: "Thứ 4", 5: "Thứ 5", 6: "Thứ 6", 7: "Thứ 7", 8: "Chủ nhật"}
    week_start = None
    for row in rows:
        try:
            day = int(row.get("day_of_week") or 0)
        except (TypeError, ValueError):
            continue
        study_date = row.get("study_date")
        if day in days and study_date:
            parsed = pd.to_datetime(study_date, errors="coerce")
            if not pd.isna(parsed):
                week_start = parsed - pd.Timedelta(days=day - 2)
                break
    day_labels = {
        day: f"{day_names[day]} ({(week_start + pd.Timedelta(days=day - 2)).strftime('%d/%m')})"
        if week_start is not None
        else day_names[day]
        for day in days
    }

    def overlaps(row: dict[str, Any], period: int, day: int) -> bool:
        try:
            return (
                int(row.get("day_of_week") or 0) == day
                and int(row.get("start_period") or 0) <= period <= int(row.get("end_period") or 0)
            )
        except (TypeError, ValueError):
            return False

    def event_html(row: dict[str, Any]) -> str:
        course = row.get("name_subject") or row.get("id_class") or ""
        code = row.get("id_class") or ""
        room = row.get("id_room") or row.get("id_rooms") or ""
        teacher = row.get("name_teacher") or ""
        start_time = row.get("start_time") or ""
        end_time = row.get("end_time") or ""
        time_text = f"{start_time} - {end_time}" if start_time or end_time else ""
        return (
            '<div class="event-pill">'
            f'<div class="event-title">{_escape(course)}</div>'
            f'<div class="event-sub">{_escape(code)}</div>'
            f'<div class="event-sub">Phòng: {_escape(room)}</div>'
            f'<div class="event-sub">{_escape(teacher)}</div>'
            f'<div class="event-sub">{_escape(time_text)}</div>'
            "</div>"
        )

    header = '<th class="slot-label"></th>' + "".join(f"<th>{day_labels[day]}</th>" for day in days)
    table_rows = []
    for period in range(1, 13):
        cells = [f'<td class="slot-label">Tiết {period}</td>']
        for day in days:
            matched = [row for row in rows if overlaps(row, period, day) and int(row.get("start_period") or 0) == period]
            content = "".join(event_html(row) for row in matched)
            cells.append(f"<td>{content}</td>")
        table_rows.append(f"<tr>{''.join(cells)}</tr>")
    st.markdown(
        f"""
        <table class="schedule-grid">
            <thead><tr>{header}</tr></thead>
            <tbody>{''.join(table_rows)}</tbody>
        </table>
        """,
        unsafe_allow_html=True,
    )


def records_count(data: Any) -> int:
    return len(_records(data))


def sum_field(data: Any, field: str) -> float:
    total = 0.0
    for row in _records(data):
        try:
            total += float(row.get(field) or 0)
        except (TypeError, ValueError):
            continue
    return total
