"""Helper UI dung chung cho cac trang Streamlit."""

import streamlit as st

from db.connections import SITE_CODES, SITE_NAMES


def site_label(site_code):
    return f"{site_code} - {SITE_NAMES.get(site_code, site_code)}"


def select_site(label="Chọn site", key=None, index=0):
    labels = [site_label(site_code) for site_code in SITE_CODES]
    selected = st.selectbox(label, labels, index=index, key=key)
    return selected.split(" - ")[0]


def show_dataframe(df):
    if df is None or df.empty:
        st.info("Không có dữ liệu")
    else:
        st.dataframe(df, use_container_width=True)


def show_result(success, message):
    if success:
        st.success(message)
    else:
        st.error(message)


def id_options(df, id_column="id", label_column=None):
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


def selected_id(option):
    if not option:
        return ""
    return str(option).split(" - ")[0]
