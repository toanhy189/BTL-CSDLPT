"""Trang Streamlit cho nghiệp vụ trang tổng quan, hiển thị dữ liệu và gửi thao tác của người dùng."""

import pandas as pd
import streamlit as st

from db.connections import DB_CONFIGS, SITE_CODES, SITE_NAMES, check_site_connection
from db.distributed_queries import read_all_sites
from ui_pages._helpers import metric_card, page_title, section_title, show_dataframe


# Hàm hỗ trợ chuẩn hóa/lọc/chuẩn bị dữ liệu safe count trước khi hiển thị hoặc xử lý.
def _safe_count(table_name, active_only=False):
    """Hàm hỗ trợ chuẩn hóa/lọc/chuẩn bị dữ liệu safe count trước khi hiển thị hoặc xử lý."""
    df = read_all_sites(table_name)
    if df.empty:
        return 0
    if active_only and "status" in df.columns:
        df = df[df["status"] == "DA_DANG_KY"]
    return len(df)


# Vẽ màn hình/khối giao diện trang tổng quan và gọi API hoặc service khi người dùng thao tác.
def render_dashboard_page():
    """Vẽ màn hình/khối giao diện trang tổng quan và gọi API hoặc service khi người dùng thao tác."""
    page_title(
        "📊 Tổng quan",
        "Theo dõi nhanh trạng thái 5 site PostgreSQL và dữ liệu toàn hệ thống.",
    )

    students_count = _safe_count("sinhvien")
    classes_count = _safe_count("lophocphan")
    registrations_count = _safe_count("dangky", active_only=True)

    cols = st.columns(5)
    metrics = [
        ("Số cơ sở", 5),
        ("Server PostgreSQL", 5),
        ("Tổng sinh viên", students_count),
        ("Tổng lớp học phần", classes_count),
        ("Lượt đăng ký", registrations_count),
    ]
    for col, (label, value) in zip(cols, metrics):
        with col:
            metric_card(label, value)

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
                "status": "OK" if ok else "ERROR",
                "message": message,
            }
        )
        if not ok:
            failed_sites.append(site_code)

    if failed_sites:
        st.warning("Một số site không kết nối được: " + ", ".join(failed_sites))

    section_title("Trạng thái kết nối 5 site", "Ứng dụng kiểm tra trực tiếp qua psycopg2.")
    show_dataframe(pd.DataFrame(rows), height=240)

    section_title("Kiến trúc hệ thống")
    st.markdown(
        """
        - Mỗi cơ sở là một PostgreSQL server/container riêng.
        - Dữ liệu cục bộ như sinh viên, giảng viên, phòng học, lớp học phần nằm tại site tương ứng.
        - Dữ liệu dùng chung như học phần được nhân bản trên các site.
        - Truy vấn toàn trường đọc từ 5 site rồi tổng hợp bằng pandas.
        """
    )
