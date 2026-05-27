"""Trang Streamlit cho nghiệp vụ trang truy vấn phân tán, hiển thị dữ liệu và gửi thao tác của người dùng."""

import streamlit as st

from ui_pages._helpers import page_title, section_title, show_dataframe
from services import distributed_query_service as service


# Xử lý bước nghiệp vụ run query trong module này.
def _run_query(button_key, query_func, chart_column=None, index_column=None):
    """Xử lý bước nghiệp vụ run query trong module này."""
    if st.button("Chạy truy vấn", key=button_key):
        df = query_func()
        show_dataframe(df, height=430)
        if chart_column and index_column and not df.empty:
            st.bar_chart(df.set_index(index_column)[chart_column])


# Vẽ màn hình/khối giao diện trang truy vấn phân tán và gọi API hoặc service khi người dùng thao tác.
def render_distributed_query_page():
    """Vẽ màn hình/khối giao diện trang truy vấn phân tán và gọi API hoặc service khi người dùng thao tác."""
    page_title(
        "📈 Truy vấn phân tán / Thống kê",
        "Đọc dữ liệu từ 5 PostgreSQL site và tổng hợp bằng pandas.",
    )

    tabs = st.tabs(
        [
            "Đăng ký theo cơ sở",
            "Top học phần",
            "Đăng ký chéo",
            "Tỷ lệ lấp đầy",
            "Số lớp",
            "Số sinh viên",
            "Danh sách lớp",
        ]
    )

    with tabs[0]:
        section_title("Đăng ký theo cơ sở", "Gộp lophocphan và dangky từ 5 site.")
        with st.expander("Mô tả truy vấn", expanded=False):
            st.write("Mỗi site tự thống kê số lượt đăng ký theo cơ sở mở lớp, sau đó pandas cộng kết quả toàn hệ thống.")
        _run_query(
            "q_dang_ky_co_so",
            service.thong_ke_dang_ky_theo_co_so,
            "so_luot_dang_ky",
            "id_headquarter",
        )

    with tabs[1]:
        section_title("Top học phần", "Tìm học phần có nhiều lượt đăng ký nhất toàn trường.")
        with st.expander("Mô tả truy vấn", expanded=False):
            st.write("Đọc hocphan, lophocphan, dangky ở 5 site rồi group theo học phần.")
        _run_query("q_top_hoc_phan", service.hoc_phan_dang_ky_nhieu_nhat, "so_luot", "name_subject")

    with tabs[2]:
        section_title("Đăng ký chéo cơ sở", "Sinh viên đăng ký lớp tại cơ sở khác.")
        with st.expander("Mô tả truy vấn", expanded=False):
            st.write("Lọc các bản ghi có cơ sở sinh viên khác cơ sở mở lớp.")
        _run_query("q_dang_ky_cheo", service.sinh_vien_dang_ky_cheo_co_so)

    with tabs[3]:
        section_title("Tỷ lệ lấp đầy", "Tính number_of_student / max_student cho từng lớp.")
        with st.expander("Mô tả truy vấn", expanded=False):
            st.write("Mỗi site trả tỷ lệ lấp đầy của các lớp học phần tại site đó.")
        _run_query("q_lap_day", service.ty_le_lap_day_lop_hoc_phan)

    with tabs[4]:
        section_title("Số lớp theo cơ sở", "Thống kê số lớp học phần mở tại từng cơ sở.")
        _run_query("q_so_lop", service.thong_ke_so_lop_theo_co_so, "so_lop_mo", "id_headquarter")

    with tabs[5]:
        section_title("Số sinh viên theo cơ sở", "Thống kê số sinh viên phân mảnh theo site.")
        _run_query(
            "q_so_sinh_vien",
            service.thong_ke_sinh_vien_theo_co_so,
            "so_sinh_vien",
            "id_headquarter",
        )

    with tabs[6]:
        section_title("Danh sách lớp toàn trường", "Kèm danh sách phòng học lấy qua bảng LichHoc.")
        _run_query("q_danh_sach_lop", service.danh_sach_lop_hoc_phan_toan_truong)
