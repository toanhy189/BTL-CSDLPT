"""Bộ helper giao diện Streamlit: CSS, header, card, bảng, badge và lịch học."""

from __future__ import annotations

import html
from collections.abc import Iterable
from typing import Any

import pandas as pd
import streamlit as st


ROLE_LABELS = {
    "ADMIN": "Admin",
    "GIANG_VIEN": "Giảng viên",
    "SINH_VIEN": "Sinh viên",
}

ROLE_PORTALS = {
    "ADMIN": "Cổng quản trị",
    "GIANG_VIEN": "Cổng giảng viên",
    "SINH_VIEN": "Cổng sinh viên",
}

SITE_LABELS = {
    "HL": "Cơ sở Hà Nội",
    "NT": "Cơ sở Đà Nẵng",
    "HD": "Cơ sở TP. Hồ Chí Minh",
    "CG": "Phân hiệu Cần Thơ",
    "HCM": "Phân hiệu Hải Phòng",
}


# Escape dữ liệu trước khi nhúng vào HTML để tránh vỡ giao diện.
def _escape(value: Any) -> str:
    """Escape dữ liệu trước khi nhúng vào HTML để tránh vỡ giao diện."""
    if value is None:
        return ""
    return html.escape(str(value))


# Định dạng số theo kiểu dễ đọc trước khi đưa vào card hoặc bảng.
def _number(value: Any) -> str:
    """Định dạng số theo kiểu dễ đọc trước khi đưa vào card hoặc bảng."""
    try:
        if isinstance(value, str) and not value.strip():
            return "0"
        number = float(value)
    except (TypeError, ValueError):
        return _escape(value)

    if number.is_integer():
        return f"{int(number):,}".replace(",", ".")
    return f"{number:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# Chuẩn hóa DataFrame, dict hoặc list thành danh sách record cho component HTML.
def _records(data: Any) -> list[dict[str, Any]]:
    """Chuẩn hóa DataFrame, dict hoặc list thành danh sách record cho component HTML."""
    if data is None or (isinstance(data, dict) and data.get("_error")):
        return []
    if isinstance(data, pd.DataFrame):
        return data.astype(object).where(pd.notnull(data), None).to_dict(orient="records")
    if isinstance(data, dict):
        return [data]
    if isinstance(data, Iterable) and not isinstance(data, (str, bytes)):
        return [row for row in data if isinstance(row, dict)]
    return []


# Nạp CSS tùy biến cho toàn bộ frontend Streamlit.
def load_styles() -> None:
    """Nạp CSS tùy biến cho toàn bộ frontend Streamlit."""
    st.markdown(
        """
        <style>
        :root {
            --red: #d71920;
            --red-dark: #b11226;
            --red-soft: #fff1f2;
            --red-pale: #fff6f7;
            --blue: #1d4ed8;
            --blue-dark: #173b70;
            --green: #16a34a;
            --orange: #f59e0b;
            --purple: #7c3aed;
            --ink: #101828;
            --text: #1f2937;
            --muted: #667085;
            --line: #e4e7ec;
            --bg: #f7f8fb;
            --card: #ffffff;
            --shadow: 0 8px 24px rgba(16, 24, 40, .07);
            --shadow-soft: 0 2px 10px rgba(16, 24, 40, .05);
        }

        #MainMenu, footer, header { visibility: hidden; }

        .stApp {
            background: var(--bg);
            color: var(--text);
            font-family: "Inter", "Segoe UI", Arial, sans-serif;
        }

        .block-container {
            max-width: 1600px;
            padding: 0.85rem 1.35rem 2rem 1.35rem;
        }

        h1, h2, h3, h4, h5, h6, p, label, span, div {
            letter-spacing: 0;
        }

        [data-testid="stSidebar"] {
            background: #ffffff;
            border-right: 1px solid var(--line);
            box-shadow: 3px 0 18px rgba(16, 24, 40, .03);
        }

        [data-testid="stSidebar"] > div:first-child {
            padding: 1rem 1rem 1.2rem 1rem;
        }

        .sidebar-brand {
            display: flex;
            align-items: center;
            gap: 13px;
            padding: 6px 2px 18px 2px;
            border-bottom: 1px solid var(--line);
            margin-bottom: 16px;
        }

        .logo-square {
            width: 50px;
            height: 50px;
            border-radius: 10px;
            background: linear-gradient(135deg, #e73a4b 0%, #c70718 100%);
            color: white;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 10px 22px rgba(215, 25, 32, .24);
            position: relative;
            flex: 0 0 auto;
        }

        .logo-square::before,
        .logo-square::after {
            content: "";
            width: 12px;
            height: 20px;
            border: 2px solid #fff;
            border-radius: 2px 6px 6px 2px;
            background: rgba(255,255,255,.12);
            position: absolute;
            top: 15px;
        }

        .logo-square::before {
            left: 12px;
            transform: skewY(4deg);
        }

        .logo-square::after {
            right: 12px;
            transform: scaleX(-1) skewY(4deg);
        }

        .sidebar-title {
            color: var(--red-dark);
            font-weight: 900;
            line-height: 1.15;
            font-size: 14px;
            text-transform: uppercase;
        }

        .sidebar-subtitle {
            color: var(--muted);
            font-size: 12px;
            margin-top: 4px;
        }

        .sidebar-group {
            color: var(--red);
            font-size: 11px;
            font-weight: 900;
            text-transform: uppercase;
            margin: 18px 4px 8px 4px;
        }

        [data-testid="stSidebar"] .stRadio > label {
            display: none;
        }

        [data-testid="stSidebar"] div[role="radiogroup"] {
            gap: 6px;
        }

        [data-testid="stSidebar"] div[role="radiogroup"] label {
            min-height: 46px;
            padding: 9px 12px;
            border-radius: 8px;
            color: #344054;
            font-weight: 700;
            border-left: 4px solid transparent;
        }

        [data-testid="stSidebar"] div[role="radiogroup"] label:hover {
            background: #f9fafb;
        }

        [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
            background: linear-gradient(90deg, #fff1f2 0%, #fff8f9 100%);
            color: var(--red-dark);
            border-left-color: var(--red);
        }

        [data-testid="stSidebar"] .stButton button {
            width: 100%;
        }

        .support-box {
            margin-top: 28px;
            padding: 15px;
            background: linear-gradient(135deg, #fff7f8 0%, #ffffff 100%);
            border: 1px solid #fde2e5;
            border-radius: 8px;
            color: #344054;
            font-size: 13px;
        }

        .support-title {
            font-weight: 850;
            color: #1f2937;
            margin-bottom: 8px;
        }

        .portal-header {
            min-height: 72px;
            background: #ffffff;
            border-bottom: 1px solid var(--line);
            box-shadow: var(--shadow-soft);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 12px 18px;
            margin: -0.85rem -1.35rem 20px -1.35rem;
        }

        .brand {
            display: flex;
            align-items: center;
            gap: 14px;
        }

        .brand-title {
            color: var(--red-dark);
            font-size: 19px;
            font-weight: 900;
            line-height: 1.15;
            text-transform: uppercase;
        }

        .brand-subtitle {
            color: var(--muted);
            font-size: 13px;
            margin-top: 4px;
        }

        .top-actions {
            display: flex;
            align-items: center;
            gap: 18px;
        }

        .bell {
            position: relative;
            width: 34px;
            height: 34px;
            border-radius: 999px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            color: #475467;
            border: 1px solid transparent;
        }

        .bell::before {
            content: "";
            width: 13px;
            height: 15px;
            border: 2px solid currentColor;
            border-radius: 9px 9px 5px 5px;
            border-bottom-width: 1px;
        }

        .bell::after {
            content: "";
            position: absolute;
            bottom: 6px;
            width: 8px;
            height: 2px;
            border-radius: 999px;
            background: currentColor;
        }

        .bell-badge {
            position: absolute;
            top: -1px;
            right: -1px;
            background: var(--red);
            color: white;
            min-width: 18px;
            height: 18px;
            padding: 0 5px;
            border-radius: 99px;
            font-size: 11px;
            line-height: 18px;
            text-align: center;
            font-weight: 850;
        }

        .user-pill {
            display: flex;
            align-items: center;
            gap: 10px;
            padding-left: 12px;
            border-left: 1px solid var(--line);
        }

        .avatar {
            background: linear-gradient(135deg, #ee4556, #c9152a);
            color: white;
            width: 42px;
            height: 42px;
            border-radius: 999px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-weight: 900;
            box-shadow: 0 8px 18px rgba(215, 25, 32, .18);
        }

        .user-name {
            color: #111827;
            font-weight: 850;
            font-size: 14px;
        }

        .user-role {
            color: var(--muted);
            font-size: 12px;
            margin-top: 2px;
        }

        .chevron {
            width: 8px;
            height: 8px;
            border-right: 2px solid #667085;
            border-bottom: 2px solid #667085;
            transform: rotate(45deg);
            margin-left: 6px;
        }

        .page-title-wrap {
            display: flex;
            align-items: flex-start;
            gap: 14px;
            margin: 6px 0 14px 0;
        }

        .title-bar {
            width: 4px;
            min-height: 32px;
            background: #d0d5dd;
            border-radius: 4px;
            margin-top: 4px;
        }

        .page-title {
            font-size: 26px;
            font-weight: 900;
            color: #101828;
            line-height: 1.2;
        }

        .page-subtitle {
            color: var(--muted);
            font-size: 14px;
            margin-top: 5px;
        }

        .section-card,
        div[data-testid="stVerticalBlock"]:has(.card-surface-marker) {
            background: var(--card);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 16px 18px;
            box-shadow: var(--shadow-soft);
            margin: 12px 0;
        }

        .section-head {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 14px;
            margin-bottom: 12px;
        }

        .section-title {
            font-size: 17px;
            font-weight: 900;
            color: #111827;
        }

        .section-subtitle {
            color: var(--muted);
            font-size: 13px;
            margin-top: 3px;
        }

        .metric-card {
            background: var(--card);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 18px;
            box-shadow: var(--shadow-soft);
            min-height: 112px;
            display: flex;
            align-items: center;
            gap: 14px;
        }

        .metric-icon {
            width: 54px;
            height: 54px;
            border-radius: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 26px;
            background: #fff1f2;
            color: var(--red);
            flex: 0 0 auto;
            font-weight: 900;
        }

        .metric-icon.blue { background: #eff6ff; color: #2563eb; }
        .metric-icon.green { background: #ecfdf3; color: #16a34a; }
        .metric-icon.orange { background: #fff7ed; color: #f59e0b; }
        .metric-icon.purple { background: #f5f3ff; color: #7c3aed; }
        .metric-icon.gray { background: #f2f4f7; color: #475467; }

        .metric-label {
            color: #475467;
            font-size: 13px;
            font-weight: 750;
        }

        .metric-value {
            color: #101828;
            font-size: 26px;
            font-weight: 950;
            line-height: 1.1;
            margin-top: 5px;
        }

        .metric-value.red { color: var(--red); }

        .metric-note {
            color: var(--green);
            font-size: 12px;
            font-weight: 750;
            margin-top: 8px;
        }

        .mini-note {
            color: var(--muted);
            font-size: 12px;
            margin-top: 7px;
        }

        .filter-panel {
            background: #ffffff;
            border: 1px solid var(--line);
            border-radius: 8px;
            box-shadow: var(--shadow-soft);
            padding: 13px 16px 4px 16px;
            margin: 0 0 14px 0;
        }

        .inline-actions {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }

        div.stButton > button,
        div[data-testid="stFormSubmitButton"] button {
            border-radius: 6px;
            border: 1px solid var(--red);
            background: var(--red);
            color: white;
            font-weight: 850;
            min-height: 38px;
            box-shadow: none;
        }

        div.stButton > button:hover,
        div[data-testid="stFormSubmitButton"] button:hover {
            border-color: var(--red-dark);
            background: var(--red-dark);
            color: #fff;
        }

        div.stButton > button[kind="secondary"] {
            background: white;
            color: var(--red);
        }

        .stTextInput input,
        .stNumberInput input,
        .stDateInput input,
        .stTextArea textarea,
        .stSelectbox div[data-baseweb="select"] {
            border-radius: 6px;
        }

        .stTextInput label,
        .stNumberInput label,
        .stDateInput label,
        .stTextArea label,
        .stSelectbox label {
            color: #1f2937;
            font-weight: 750;
            font-size: 13px;
        }

        [data-testid="stDataFrame"] {
            border: 1px solid var(--line);
            border-radius: 8px;
            overflow: hidden;
            box-shadow: none;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            border-bottom: 1px solid var(--line);
        }

        .stTabs [data-baseweb="tab"] {
            padding: 13px 18px;
            font-weight: 850;
        }

        .stTabs [aria-selected="true"] {
            color: var(--red-dark);
            border-bottom: 2px solid var(--red);
        }

        .ui-table-wrap {
            border: 1px solid var(--line);
            border-radius: 8px;
            overflow: hidden;
            background: white;
        }

        .ui-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }

        .ui-table th {
            text-align: left;
            background: #f8fafc;
            color: #1f2937;
            font-weight: 850;
            padding: 10px 12px;
            border-bottom: 1px solid var(--line);
            white-space: nowrap;
        }

        .ui-table td {
            padding: 10px 12px;
            border-bottom: 1px solid var(--line);
            color: #111827;
            vertical-align: middle;
        }

        .ui-table tr:last-child td {
            border-bottom: 0;
        }

        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            border-radius: 999px;
            padding: 4px 10px;
            font-size: 12px;
            font-weight: 850;
            border: 1px solid transparent;
            white-space: nowrap;
        }

        .status-ok {
            color: #067647;
            background: #ecfdf3;
            border-color: #abefc6;
        }

        .status-warn {
            color: #b54708;
            background: #fffaeb;
            border-color: #fedf89;
        }

        .status-error {
            color: #b42318;
            background: #fef3f2;
            border-color: #fecdca;
        }

        .progress-track {
            width: 120px;
            height: 7px;
            border-radius: 99px;
            background: #e4e7ec;
            overflow: hidden;
        }

        .progress-fill {
            height: 100%;
            border-radius: 99px;
            background: #16a34a;
        }

        .progress-fill.warn { background: #f59e0b; }
        .progress-fill.danger { background: #d71920; }

        .schedule-grid {
            width: 100%;
            border-collapse: collapse;
            table-layout: fixed;
            font-size: 13px;
            border: 1px solid var(--line);
            border-radius: 8px;
            overflow: hidden;
        }

        .schedule-grid th,
        .schedule-grid td {
            border: 1px solid var(--line);
            padding: 10px;
            min-height: 74px;
            vertical-align: top;
            background: white;
        }

        .schedule-grid th {
            text-align: center;
            background: #f8fafc;
            font-weight: 900;
        }

        .slot-label {
            width: 96px;
            color: #344054;
            font-weight: 850;
            text-align: center;
        }

        .event-pill {
            border-radius: 6px;
            padding: 8px 9px;
            line-height: 1.35;
            font-weight: 750;
            text-align: center;
            border: 1px solid #fecaca;
            background: #fff1f2;
            color: #b11226;
            margin-bottom: 6px;
        }

        .event-pill.green {
            border-color: #bbf7d0;
            background: #f0fdf4;
            color: #15803d;
        }

        .event-pill.blue {
            border-color: #bfdbfe;
            background: #eff6ff;
            color: #1d4ed8;
        }

        .event-pill.orange {
            border-color: #fed7aa;
            background: #fff7ed;
            color: #c2410c;
        }

        .event-pill.purple {
            border-color: #ddd6fe;
            background: #f5f3ff;
            color: #7c3aed;
        }

        .empty-state {
            border: 1px dashed #cbd5e1;
            border-radius: 8px;
            padding: 20px;
            color: var(--muted);
            text-align: center;
            background: #fff;
        }

        .login-page-marker {
            display: none;
        }

        .stApp:has(.login-page-marker) [data-testid="stSidebar"] {
            display: none;
        }

        .stApp:has(.login-page-marker) .block-container {
            max-width: none;
            min-height: 100vh;
            overflow: hidden;
            padding: 56px 64px 96px 64px;
            position: relative;
        }

        .stApp:has(.login-page-marker) {
            background:
                linear-gradient(90deg, rgba(255,255,255,.96) 0%, rgba(255,255,255,.72) 46%, rgba(255,255,255,.98) 100%),
                radial-gradient(circle at 33% 14%, rgba(191,226,255,.82) 0, transparent 34%),
                linear-gradient(180deg, #cfe9ff 0%, #eef7ff 44%, #ffffff 100%);
        }

        .stApp:has(.login-page-marker) .block-container::before {
            content: "";
            position: absolute;
            left: -2%;
            right: 36%;
            bottom: 84px;
            height: 50vh;
            min-height: 390px;
            background:
                linear-gradient(180deg, rgba(255,255,255,.05), rgba(255,255,255,.86)),
                repeating-linear-gradient(90deg, transparent 0 24px, rgba(23,59,112,.26) 25px 38px, transparent 39px 76px),
                linear-gradient(90deg, #f3eee7 0 18%, #d7cabb 18% 20%, #f6f0e8 20% 50%, #cdd7df 50% 53%, #f2eee6 53% 100%);
            border-radius: 12px 12px 0 0;
            box-shadow: inset 0 0 0 2px rgba(255,255,255,.48);
            clip-path: polygon(0 40%, 18% 22%, 34% 36%, 43% 5%, 57% 5%, 66% 36%, 82% 22%, 100% 40%, 100% 100%, 0 100%);
            z-index: 0;
        }

        .stApp:has(.login-page-marker) .block-container::after {
            content: "";
            position: absolute;
            left: 0;
            right: 0;
            bottom: 0;
            height: 84px;
            background: linear-gradient(180deg, #df0f1d, #b60815);
            z-index: 1;
        }

        .stApp:has(.login-page-marker) [data-testid="stVerticalBlock"],
        .stApp:has(.login-page-marker) [data-testid="column"] {
            position: relative;
            z-index: 2;
        }

        .login-layout {
            min-height: 100vh;
            position: relative;
            overflow: hidden;
            padding: 56px 64px 96px 64px;
        }

        .login-layout::before {
            content: "";
            position: absolute;
            left: -2%;
            right: 36%;
            bottom: 84px;
            height: 50vh;
            min-height: 390px;
            background:
                linear-gradient(180deg, rgba(255,255,255,.05), rgba(255,255,255,.86)),
                repeating-linear-gradient(90deg, transparent 0 24px, rgba(23,59,112,.26) 25px 38px, transparent 39px 76px),
                linear-gradient(90deg, #f3eee7 0 18%, #d7cabb 18% 20%, #f6f0e8 20% 50%, #cdd7df 50% 53%, #f2eee6 53% 100%);
            border-radius: 12px 12px 0 0;
            box-shadow: inset 0 0 0 2px rgba(255,255,255,.48);
            clip-path: polygon(0 40%, 18% 22%, 34% 36%, 43% 5%, 57% 5%, 66% 36%, 82% 22%, 100% 40%, 100% 100%, 0 100%);
            z-index: 0;
        }

        .login-layout::after {
            content: "";
            position: absolute;
            left: 0;
            right: 0;
            bottom: 0;
            height: 84px;
            background: linear-gradient(180deg, #df0f1d, #b60815);
            z-index: 1;
        }

        .login-content {
            position: relative;
            z-index: 2;
            display: grid;
            grid-template-columns: 1.28fr .72fr;
            gap: 56px;
            align-items: center;
            min-height: calc(100vh - 152px);
        }

        .login-title {
            color: var(--red-dark);
            font-size: clamp(34px, 3.2vw, 58px);
            line-height: 1.08;
            font-weight: 950;
            text-transform: uppercase;
            max-width: 980px;
        }

        .login-subtitle {
            margin-top: 22px;
            color: #4b5563;
            font-size: 24px;
            font-weight: 850;
        }

        .login-features {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 26px;
            margin-top: 48px;
            max-width: 900px;
        }

        .login-feature {
            display: grid;
            grid-template-columns: 44px 1fr;
            gap: 14px;
            align-items: center;
        }

        .feature-icon {
            width: 38px;
            height: 38px;
            color: var(--red-dark);
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: 8px;
            font-size: 24px;
            font-weight: 900;
        }

        .feature-title {
            font-weight: 900;
            color: #111827;
            font-size: 17px;
        }

        .feature-sub {
            color: #4b5563;
            font-size: 14px;
            margin-top: 4px;
        }

        .login-form-shell {
            background: rgba(255,255,255,.94);
            border: 1px solid rgba(203, 213, 225, .95);
            border-radius: 16px;
            box-shadow: 0 22px 45px rgba(15, 23, 42, .18);
            padding: 34px;
            backdrop-filter: blur(8px);
        }

        div[data-testid="stVerticalBlock"]:has(.login-form-panel) {
            background: rgba(255,255,255,.94);
            border: 1px solid rgba(203, 213, 225, .95);
            border-radius: 16px;
            box-shadow: 0 22px 45px rgba(15, 23, 42, .18);
            padding: 34px;
            backdrop-filter: blur(8px);
        }

        .login-card-title {
            text-align: center;
            color: var(--red-dark);
            font-size: 24px;
            font-weight: 950;
            text-transform: uppercase;
            margin-bottom: 8px;
        }

        .login-card-sub {
            text-align: center;
            color: #667085;
            font-size: 14px;
            margin-bottom: 26px;
        }

        .login-form-shell .stButton button,
        .login-form-shell div[data-testid="stFormSubmitButton"] button,
        div[data-testid="stVerticalBlock"]:has(.login-form-panel) div[data-testid="stFormSubmitButton"] button {
            width: 100%;
            min-height: 52px;
            font-size: 16px;
            border-radius: 7px;
        }

        .login-form-shell .stTextInput input,
        div[data-testid="stVerticalBlock"]:has(.login-form-panel) .stTextInput input {
            min-height: 46px;
        }

        .login-secondary {
            margin-top: 12px;
            border: 1px solid var(--line);
            border-radius: 7px;
            min-height: 48px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #111827;
            font-weight: 850;
        }

        .forgot-link {
            margin-top: 22px;
            text-align: center;
            color: var(--red);
            text-decoration: underline;
            font-weight: 750;
        }

        .login-footer-text {
            position: absolute;
            left: 0;
            right: 0;
            bottom: 13px;
            z-index: 3;
            text-align: center;
            color: white;
            font-weight: 900;
            letter-spacing: .4px;
            text-transform: uppercase;
            font-size: 18px;
        }

        .login-footer-sub {
            display: block;
            font-size: 13px;
            font-weight: 500;
            text-transform: none;
            margin-top: 5px;
            opacity: .9;
        }

        @media (max-width: 1100px) {
            .portal-header {
                flex-direction: column;
                align-items: flex-start;
                gap: 12px;
            }

            .login-layout {
                padding: 34px 20px 104px 20px;
            }

            .stApp:has(.login-page-marker) .block-container {
                padding: 34px 20px 104px 20px;
            }

            .login-content {
                grid-template-columns: 1fr;
                gap: 24px;
            }

            .login-features {
                grid-template-columns: 1fr;
                margin-top: 28px;
            }

            .login-layout::before {
                right: 0;
                opacity: .45;
            }

            .stApp:has(.login-page-marker) .block-container::before {
                right: 0;
                opacity: .45;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# Nạp CSS riêng cho màn hình đăng nhập.
def login_mode_css() -> None:
    """Nạp CSS riêng cho màn hình đăng nhập."""
    st.markdown('<div class="login-page-marker"></div>', unsafe_allow_html=True)


# Tạo tên cổng chức năng dựa trên vai trò của người dùng đang đăng nhập.
def role_portal(user: dict[str, Any] | None) -> str:
    """Tạo tên cổng chức năng dựa trên vai trò của người dùng đang đăng nhập."""
    if not user:
        return "Cổng quản lý đào tạo"
    return ROLE_PORTALS.get(user.get("role", ""), "Cổng quản lý đào tạo")


# Vẽ màn hình/khối giao diện header và gọi API hoặc service khi người dùng thao tác.
def render_header(user: dict[str, Any] | None = None, subtitle: str = "Cổng quản lý đào tạo") -> None:
    """Vẽ màn hình/khối giao diện header và gọi API hoặc service khi người dùng thao tác."""
    name = "Khách"
    role = ""
    initials = "?"
    badge = 3
    if user:
        name = user.get("full_name") or user.get("username") or "Người dùng"
        role = ROLE_LABELS.get(user.get("role", ""), user.get("role", ""))
        initials_source = user.get("username") or name
        initials = (initials_source[:2] or "?").upper()
        badge = 5 if user.get("role") == "ADMIN" else 3

    st.markdown(
        f"""
        <div class="portal-header">
            <div class="brand">
                <div class="logo-square"></div>
                <div>
                    <div class="brand-title">Hệ thống đăng ký học phần nhiều cơ sở</div>
                    <div class="brand-subtitle">{_escape(subtitle)}</div>
                </div>
            </div>
            <div class="top-actions">
                <div class="bell"><span class="bell-badge">{badge}</span></div>
                <div class="user-pill">
                    <div class="avatar">{_escape(initials)}</div>
                    <div>
                        <div class="user-name">{_escape(name)}</div>
                        <div class="user-role">{_escape(role)}</div>
                    </div>
                    <div class="chevron"></div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# Vẽ màn hình/khối giao diện sidebar brand và gọi API hoặc service khi người dùng thao tác.
def render_sidebar_brand(subtitle: str) -> None:
    """Vẽ màn hình/khối giao diện sidebar brand và gọi API hoặc service khi người dùng thao tác."""
    st.sidebar.markdown(
        f"""
        <div class="sidebar-brand">
            <div class="logo-square"></div>
            <div>
                <div class="sidebar-title">Hệ thống đăng ký học phần nhiều cơ sở</div>
                <div class="sidebar-subtitle">{_escape(subtitle)}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# Vẽ màn hình/khối giao diện support box và gọi API hoặc service khi người dùng thao tác.
def render_support_box(role: str) -> None:
    """Vẽ màn hình/khối giao diện support box và gọi API hoặc service khi người dùng thao tác."""
    title = {
        "ADMIN": "Hỗ trợ quản trị",
        "GIANG_VIEN": "Hỗ trợ giảng viên",
        "SINH_VIEN": "Hỗ trợ sinh viên",
    }.get(role, "Hỗ trợ")
    st.sidebar.markdown(
        f"""
        <div class="support-box">
            <div class="support-title">{_escape(title)}</div>
            <div>(028) 7102 9999</div>
            <div style="margin-top:6px;">support@university.edu.vn</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# Xử lý bước nghiệp vụ page title trong module này.
def page_title(title: str, subtitle: str | None = None) -> None:
    """Xử lý bước nghiệp vụ page title trong module này."""
    subtitle_html = f'<div class="page-subtitle">{_escape(subtitle)}</div>' if subtitle else ""
    st.markdown(
        f"""
        <div class="page-title-wrap">
            <div class="title-bar"></div>
            <div>
                <div class="page-title">{_escape(title)}</div>
                {subtitle_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# Xử lý bước nghiệp vụ section title trong module này.
def section_title(title: str, subtitle: str | None = None, right: str | None = None) -> None:
    """Xử lý bước nghiệp vụ section title trong module này."""
    subtitle_html = f'<div class="section-subtitle">{_escape(subtitle)}</div>' if subtitle else ""
    right_html = f"<div>{right}</div>" if right else ""
    st.markdown(
        f"""
        <div class="section-head">
            <div>
                <div class="section-title">{_escape(title)}</div>
                {subtitle_html}
            </div>
            {right_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


# Xử lý bước nghiệp vụ metric card trong module này.
def metric_card(
    label: str,
    value: Any,
    icon: str = "▣",
    accent: str = "red",
    note: str | None = None,
    red_value: bool = False,
) -> None:
    """Xử lý bước nghiệp vụ metric card trong module này."""
    note_html = f'<div class="metric-note">{_escape(note)}</div>' if note else ""
    value_class = " red" if red_value else ""
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-icon {_escape(accent)}">{_escape(icon)}</div>
            <div>
                <div class="metric-label">{_escape(label)}</div>
                <div class="metric-value{value_class}">{_number(value)}</div>
                {note_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# Xử lý bước nghiệp vụ marker card trong module này.
def marker_card() -> None:
    """Xử lý bước nghiệp vụ marker card trong module này."""
    st.markdown('<div class="card-surface-marker"></div>', unsafe_allow_html=True)


# Xử lý bước nghiệp vụ filter panel trong module này.
def filter_panel(title: str | None = None) -> None:
    """Xử lý bước nghiệp vụ filter panel trong module này."""
    title_html = f'<div class="section-title" style="margin-bottom:8px;">{_escape(title)}</div>' if title else ""
    st.markdown(f'<div class="filter-panel">{title_html}</div>', unsafe_allow_html=True)


# Xử lý bước nghiệp vụ dataframe trong module này.
def dataframe(data: Any, height: int = 420, rename: dict[str, str] | None = None, columns: list[str] | None = None) -> None:
    """Xử lý bước nghiệp vụ dataframe trong module này."""
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


# Xử lý bước nghiệp vụ status class trong module này.
def _status_class(value: Any) -> str:
    """Xử lý bước nghiệp vụ status class trong module này."""
    normalized = str(value or "").upper()
    if normalized in {"OK", "DA_DANG_KY", "ĐÃ ĐĂNG KÝ", "ACTIVE", "SUCCESS", "THÀNH CÔNG"}:
        return "status-ok"
    if normalized in {"ERROR", "FAILED", "HUY", "ĐÃ HỦY", "THẤT BẠI"}:
        return "status-error"
    return "status-warn"


# Xử lý bước nghiệp vụ status badge trong module này.
def status_badge(value: Any, label: str | None = None) -> str:
    """Xử lý bước nghiệp vụ status badge trong module này."""
    shown = label or str(value or "Đang xử lý")
    return f'<span class="status-badge {_status_class(value)}">{_escape(shown)}</span>'


# Xử lý bước nghiệp vụ progress bar trong module này.
def progress_bar(current: Any, maximum: Any) -> str:
    """Xử lý bước nghiệp vụ progress bar trong module này."""
    try:
        cur = float(current or 0)
        max_value = float(maximum or 0)
        percent = 0 if max_value <= 0 else max(0, min(100, cur / max_value * 100))
    except (TypeError, ValueError):
        percent = 0
    tone = "danger" if percent >= 95 else "warn" if percent >= 80 else ""
    return (
        f'<div class="progress-track"><div class="progress-fill {tone}" '
        f'style="width:{percent:.0f}%"></div></div>'
    )


# Xử lý bước nghiệp vụ html table trong module này.
def html_table(
    data: Any,
    columns: list[tuple[str, str]],
    limit: int | None = 10,
    empty: str = "Không có dữ liệu",
    status_columns: set[str] | None = None,
    progress: tuple[str, str] | None = None,
) -> None:
    """Xử lý bước nghiệp vụ html table trong module này."""
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


# Xử lý bước nghiệp vụ lịch học grid trong module này.
def schedule_grid(data: Any, title: str = "Thời khóa biểu") -> None:
    """Xử lý bước nghiệp vụ lịch học grid trong module này."""
    rows = _records(data)
    section_title(title)
    if not rows:
        st.markdown('<div class="empty-state">Chưa có lịch học</div>', unsafe_allow_html=True)
        return

    days = [2, 3, 4, 5, 6, 7]
    bands = [("Sáng", 1, 4), ("Chiều", 5, 8), ("Tối", 9, 12)]
    accents = ["red", "green", "blue", "orange", "purple"]

    # Dựng HTML cho một sự kiện lịch học/lịch dạy trong ô thời khóa biểu.
    def event_html(row: dict[str, Any], idx: int) -> str:
        """Dựng HTML cho một sự kiện lịch học/lịch dạy trong ô thời khóa biểu."""
        course = row.get("name_subject") or row.get("id_class") or row.get("id")
        code = row.get("id_class") or row.get("id") or ""
        room = row.get("id_room") or row.get("id_rooms") or ""
        start = row.get("start_period") or ""
        end = row.get("end_period") or ""
        accent = accents[idx % len(accents)]
        return (
            f'<div class="event-pill {accent}">'
            f'<div>{_escape(code)}</div>'
            f'<div>{_escape(course)}</div>'
            f'<div>Tiết {_escape(start)} - {_escape(end)}</div>'
            f'<div>{_escape(room)}</div>'
            "</div>"
        )

    header = '<th class="slot-label">Buổi</th>' + "".join(f"<th>Thứ {day}</th>" for day in days)
    table_rows = []
    for label, start_min, start_max in bands:
        cells = [f'<td class="slot-label">{_escape(label)}</td>']
        for day in days:
            matched = [
                row
                for row in rows
                if int(row.get("day_of_week") or 0) == day
                and start_min <= int(row.get("start_period") or 0) <= start_max
            ]
            content = "".join(event_html(row, idx) for idx, row in enumerate(matched))
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


# Xử lý bước nghiệp vụ records count trong module này.
def records_count(data: Any) -> int:
    """Xử lý bước nghiệp vụ records count trong module này."""
    return len(_records(data))


# Xử lý bước nghiệp vụ sum field trong module này.
def sum_field(data: Any, field: str) -> float:
    """Xử lý bước nghiệp vụ sum field trong module này."""
    total = 0.0
    for row in _records(data):
        try:
            total += float(row.get(field) or 0)
        except (TypeError, ValueError):
            continue
    return total
