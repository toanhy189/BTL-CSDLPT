"""Trang Streamlit cho nghiệp vụ helpers, hiển thị dữ liệu và gửi thao tác của người dùng."""

import html

import streamlit as st

from db.connections import SITE_CODES, SITE_NAMES


# Nạp CSS tùy biến cho bản Streamlit cũ.
def load_custom_css():
    """Nạp CSS tùy biến cho bản Streamlit cũ."""
    st.markdown(
        """
        <style>
        :root {
            --navy: #0f3d5e;
            --navy-2: #1f4e79;
            --red: #b11226;
            --bg: #f4f6f9;
            --card: #ffffff;
            --muted: #667085;
            --border: #d9e2ec;
        }

        #MainMenu, footer {visibility: hidden;}

        .stApp {
            background: var(--bg);
            color: #1f2937;
            font-family: "Segoe UI", Arial, sans-serif;
        }

        .block-container {
            padding-top: 1.25rem;
            padding-bottom: 2rem;
            max-width: 1500px;
        }

        [data-testid="stSidebar"] {
            background: #ffffff;
            border-right: 1px solid var(--border);
        }

        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {
            color: var(--navy);
        }

        [data-testid="stSidebar"] [role="radiogroup"] label {
            border-radius: 8px;
            padding: 0.25rem 0.35rem;
            margin-bottom: 0.15rem;
        }

        [data-testid="stSidebar"] [role="radiogroup"] label:hover {
            background: #eef5fb;
        }

        .main-header {
            background: linear-gradient(90deg, #0f3d5e 0%, #1f4e79 68%, #b11226 100%);
            color: white;
            border-radius: 10px;
            padding: 22px 26px;
            margin-bottom: 18px;
            box-shadow: 0 8px 22px rgba(15, 61, 94, 0.18);
        }

        .main-header .title {
            font-size: 25px;
            line-height: 1.25;
            font-weight: 750;
            letter-spacing: 0;
            margin: 0;
        }

        .sub-header {
            font-size: 14px;
            opacity: 0.92;
            margin-top: 6px;
        }

        .page-title {
            font-size: 23px;
            font-weight: 750;
            color: var(--navy);
            margin: 6px 0 12px 0;
        }

        .section-card {
            background: var(--card);
            border: 1px solid #edf1f5;
            border-radius: 10px;
            padding: 16px 18px;
            margin: 12px 0 16px 0;
            box-shadow: 0 3px 12px rgba(15, 61, 94, 0.06);
        }

        .section-title {
            color: var(--navy);
            font-size: 17px;
            font-weight: 720;
            margin-bottom: 4px;
        }

        .section-subtitle {
            color: var(--muted);
            font-size: 13px;
            margin-bottom: 4px;
        }

        .metric-card {
            background: var(--card);
            border-left: 5px solid var(--navy-2);
            border-radius: 10px;
            padding: 14px 16px;
            box-shadow: 0 3px 12px rgba(15, 61, 94, 0.07);
            min-height: 92px;
        }

        .metric-card .metric-label {
            color: var(--muted);
            font-size: 13px;
            font-weight: 600;
            margin-bottom: 6px;
        }

        .metric-card .metric-value {
            color: var(--navy);
            font-size: 26px;
            font-weight: 760;
        }

        .status-ok {
            color: #05603a;
            background: #ecfdf3;
            border: 1px solid #abefc6;
            padding: 3px 8px;
            border-radius: 999px;
            font-weight: 650;
        }

        .status-error {
            color: #b42318;
            background: #fef3f2;
            border: 1px solid #fecdca;
            padding: 3px 8px;
            border-radius: 999px;
            font-weight: 650;
        }

        div[data-testid="stExpander"] {
            background: #ffffff;
            border: 1px solid #e6edf3;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(15, 61, 94, 0.04);
        }

        div.stButton > button,
        div[data-testid="stFormSubmitButton"] button {
            border-radius: 8px;
            border: 1px solid #0f3d5e;
            background: #0f3d5e;
            color: white;
            font-weight: 650;
        }

        div.stButton > button:hover,
        div[data-testid="stFormSubmitButton"] button:hover {
            border-color: #b11226;
            background: #b11226;
            color: white;
        }

        [data-testid="stDataFrame"] {
            border: 1px solid #e5edf4;
            border-radius: 8px;
            overflow: hidden;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# Vẽ màn hình/khối giao diện main header và gọi API hoặc service khi người dùng thao tác.
def render_main_header():
    """Vẽ màn hình/khối giao diện main header và gọi API hoặc service khi người dùng thao tác."""
    st.markdown(
        """
        <div class="main-header">
            <div class="title">HỆ THỐNG ĐĂNG KÝ HỌC PHẦN NHIỀU CƠ SỞ</div>
            <div class="sub-header">Mô phỏng CSDL phân tán - PostgreSQL 5 site</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# Xử lý bước nghiệp vụ page title trong module này.
def page_title(title, subtitle=None):
    """Xử lý bước nghiệp vụ page title trong module này."""
    safe_title = html.escape(title)
    safe_subtitle = html.escape(subtitle or "")
    subtitle_html = f'<div class="section-subtitle">{safe_subtitle}</div>' if subtitle else ""
    st.markdown(
        f'<div class="page-title">{safe_title}</div>{subtitle_html}',
        unsafe_allow_html=True,
    )


# Xử lý bước nghiệp vụ section title trong module này.
def section_title(title, subtitle=None):
    """Xử lý bước nghiệp vụ section title trong module này."""
    safe_title = html.escape(title)
    safe_subtitle = html.escape(subtitle or "")
    subtitle_html = f'<div class="section-subtitle">{safe_subtitle}</div>' if subtitle else ""
    st.markdown(
        f"""
        <div class="section-card">
            <div class="section-title">{safe_title}</div>
            {subtitle_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


# Xử lý bước nghiệp vụ metric card trong module này.
def metric_card(label, value):
    """Xử lý bước nghiệp vụ metric card trong module này."""
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{html.escape(str(label))}</div>
            <div class="metric-value">{html.escape(str(value))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# Xử lý bước nghiệp vụ site label trong module này.
def site_label(site_code):
    """Xử lý bước nghiệp vụ site label trong module này."""
    return f"{site_code} - {SITE_NAMES.get(site_code, site_code)}"


# Xử lý bước nghiệp vụ select site trong module này.
def select_site(label="Chọn site", key=None, index=0):
    """Xử lý bước nghiệp vụ select site trong module này."""
    labels = [site_label(site_code) for site_code in SITE_CODES]
    selected = st.selectbox(label, labels, index=index, key=key)
    return selected.split(" - ")[0]


# Hiển thị bảng dữ liệu và xử lý trường hợp không có bản ghi.
def show_dataframe(df, height=None):
    """Hiển thị bảng dữ liệu và xử lý trường hợp không có bản ghi."""
    if df is None or df.empty:
        st.info("Không có dữ liệu")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True, height=height)


# Hiển thị thông báo thành công hoặc lỗi sau thao tác nghiệp vụ.
def show_result(success, message):
    """Hiển thị thông báo thành công hoặc lỗi sau thao tác nghiệp vụ."""
    if success:
        st.success(message)
    else:
        st.error(message)


# Xử lý bước nghiệp vụ id options trong module này.
def id_options(df, id_column="id", label_column=None):
    """Xử lý bước nghiệp vụ id options trong module này."""
    if df is None or df.empty or id_column not in df.columns:
        return []
    options = []
    for _, row in df.iterrows():
        value = str(row[id_column])
        if label_column and label_column in df.columns:
            options.append(f"{value} - {row[label_column]}")
        else:
            options.append(value)
    return options


# Xử lý bước nghiệp vụ selected id trong module này.
def selected_id(option):
    """Xử lý bước nghiệp vụ selected id trong module này."""
    if not option:
        return ""
    return str(option).split(" - ")[0]
