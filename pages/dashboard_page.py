"""Trang tong quan he thong."""

import pandas as pd
import streamlit as st

from db.connections import DB_CONFIGS, SITE_CODES, SITE_NAMES, check_site_connection
from db.distributed_queries import read_all_sites


def _safe_count(table_name, active_only=False):
    df = read_all_sites(table_name)
    if df.empty:
        return 0
    if active_only and "status" in df.columns:
        df = df[df["status"] == "DA_DANG_KY"]
    return len(df)


def render_dashboard_page():
    st.title("Hệ thống đăng ký học phần nhiều cơ sở")
    st.caption("Streamlit -> Python services -> psycopg2 -> 5 PostgreSQL server")

    students_count = _safe_count("sinhvien")
    classes_count = _safe_count("lophocphan")
    registrations_count = _safe_count("dangky", active_only=True)

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Số cơ sở", 5)
    col2.metric("Server PostgreSQL", 5)
    col3.metric("Tổng sinh viên", students_count)
    col4.metric("Tổng lớp học phần", classes_count)
    col5.metric("Lượt đăng ký active", registrations_count)

    rows = []
    failed_sites = []
    for site_code in SITE_CODES:
        ok, message = check_site_connection(site_code)
        config = DB_CONFIGS[site_code]
        rows.append(
            {
                "site_code": site_code,
                "site_name": SITE_NAMES.get(site_code, site_code),
                "host": config["host"],
                "port": config["port"],
                "database": config["database"],
                "status": "OK" if ok else "Lỗi",
                "message": message,
            }
        )
        if not ok:
            failed_sites.append(site_code)

    if failed_sites:
        st.warning("Một số site không kết nối được: " + ", ".join(failed_sites))

    st.subheader("Trạng thái kết nối 5 site")
    st.dataframe(pd.DataFrame(rows), use_container_width=True)

    st.subheader("Kiến trúc")
    st.markdown(
        """
        - Mỗi cơ sở là một PostgreSQL server/container riêng.
        - Dữ liệu cục bộ như sinh viên, giảng viên, phòng học, lớp học phần nằm tại site tương ứng.
        - Dữ liệu dùng chung như học phần được nhân bản trên các site.
        - Truy vấn toàn trường đọc từ 5 site rồi tổng hợp bằng pandas.
        """
    )
