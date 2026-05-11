"""Trang truy van phan tan va thong ke."""

import streamlit as st

from pages._helpers import show_dataframe
from services import distributed_query_service as service


def _run_query(button_key, query_func, chart_column=None, index_column=None):
    if st.button("Chạy truy vấn", key=button_key):
        df = query_func()
        show_dataframe(df)
        if chart_column and index_column and not df.empty:
            chart_df = df.set_index(index_column)[chart_column]
            st.bar_chart(chart_df)


def render_distributed_query_page():
    st.title("Truy vấn phân tán / Thống kê")

    tabs = st.tabs(
        [
            "Đăng ký theo cơ sở",
            "Top học phần",
            "Đăng ký chéo cơ sở",
            "Tỷ lệ lấp đầy",
            "Số lớp theo cơ sở",
            "Số sinh viên theo cơ sở",
            "Danh sách lớp toàn trường",
        ]
    )

    with tabs[0]:
        with st.expander("Mô tả truy vấn"):
            st.write("Đọc bảng lophocphan và dangky từ 5 site, sau đó group theo cơ sở mở lớp.")
        _run_query(
            "q_dang_ky_co_so",
            service.thong_ke_dang_ky_theo_co_so,
            "so_luot_dang_ky",
            "id_headquarter",
        )

    with tabs[1]:
        with st.expander("Mô tả truy vấn"):
            st.write("Đọc hocphan, lophocphan, dangky từ 5 site rồi cộng số lượt theo học phần.")
        _run_query("q_top_hoc_phan", service.hoc_phan_dang_ky_nhieu_nhat, "so_luot", "name_subject")

    with tabs[2]:
        with st.expander("Mô tả truy vấn"):
            st.write("Tìm các đăng ký có cơ sở sinh viên khác cơ sở mở lớp trên toàn bộ site.")
        _run_query("q_dang_ky_cheo", service.sinh_vien_dang_ky_cheo_co_so)

    with tabs[3]:
        with st.expander("Mô tả truy vấn"):
            st.write("Tính tỷ lệ number_of_student / max_student cho mọi lớp ở 5 site.")
        _run_query("q_lap_day", service.ty_le_lap_day_lop_hoc_phan)

    with tabs[4]:
        with st.expander("Mô tả truy vấn"):
            st.write("Đếm số lớp học phần mở tại từng cơ sở từ 5 site.")
        _run_query("q_so_lop", service.thong_ke_so_lop_theo_co_so, "so_lop_mo", "id_headquarter")

    with tabs[5]:
        with st.expander("Mô tả truy vấn"):
            st.write("Đếm số sinh viên theo cơ sở từ 5 site.")
        _run_query(
            "q_so_sinh_vien",
            service.thong_ke_sinh_vien_theo_co_so,
            "so_sinh_vien",
            "id_headquarter",
        )

    with tabs[6]:
        with st.expander("Mô tả truy vấn"):
            st.write("Lấy danh sách lớp học phần toàn trường, kèm danh sách phòng qua bảng lichhoc.")
        _run_query("q_danh_sach_lop", service.danh_sach_lop_hoc_phan_toan_truong)
