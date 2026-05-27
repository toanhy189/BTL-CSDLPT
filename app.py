"""Router chính của bản Streamlit cũ, nhận menu từ sidebar rồi gọi trang nghiệp vụ tương ứng."""

import streamlit as st

from ui_pages._helpers import load_custom_css, render_main_header
from ui_pages.cancel_page import render_cancel_page
from ui_pages.concurrency_page import render_concurrency_page
from ui_pages.dashboard_page import render_dashboard_page
from ui_pages.distributed_query_page import render_distributed_query_page
from ui_pages.log_page import render_log_page
from ui_pages.lookup_page import render_lookup_page
from ui_pages.management_page import render_management_page
from ui_pages.registration_page import render_registration_page


st.set_page_config(
    page_title="CSDL phân tán - Đăng ký học phần",
    page_icon="🎓",
    layout="wide",
)


# Danh sách menu là hợp đồng điều hướng giữa sidebar và các hàm render trang.
MENU = [
    "Tổng quan",
    "Quản lý cơ sở đào tạo",
    "Quản lý sinh viên",
    "Quản lý giảng viên",
    "Quản lý học phần",
    "Quản lý lớp học phần",
    "Quản lý phòng học và lịch học",
    "Đăng ký học phần",
    "Hủy đăng ký học phần",
    "Tra cứu kết quả đăng ký",
    "Truy vấn phân tán / Thống kê",
    "Mô phỏng đồng thời",
    "Nhật ký thao tác",
]


# Vẽ sidebar điều hướng và trả về mục menu người dùng đang chọn.
def render_sidebar():
    """Vẽ sidebar điều hướng và trả về mục menu người dùng đang chọn."""
    st.sidebar.markdown("## 🎓 CSDL phân tán")
    st.sidebar.caption("Hệ thống đăng ký học phần nhiều cơ sở")
    st.sidebar.divider()
    return st.sidebar.radio("Điều hướng", MENU, label_visibility="collapsed")


# Điểm vào của module, chuẩn bị dữ liệu/giao diện rồi điều phối sang luồng nghiệp vụ phù hợp.
def main():
    """Điểm vào của module, chuẩn bị dữ liệu/giao diện rồi điều phối sang luồng nghiệp vụ phù hợp."""
    load_custom_css()
    menu = render_sidebar()
    render_main_header()

    # Mỗi nhánh chuyển lựa chọn menu thành một trang nghiệp vụ cụ thể.
    if menu == "Tổng quan":
        render_dashboard_page()
    elif menu == "Quản lý cơ sở đào tạo":
        render_management_page("headquarters")
    elif menu == "Quản lý sinh viên":
        render_management_page("students")
    elif menu == "Quản lý giảng viên":
        render_management_page("teachers")
    elif menu == "Quản lý học phần":
        render_management_page("courses")
    elif menu == "Quản lý lớp học phần":
        render_management_page("classes")
    elif menu == "Quản lý phòng học và lịch học":
        render_management_page("rooms_schedules")
    elif menu == "Đăng ký học phần":
        render_registration_page()
    elif menu == "Hủy đăng ký học phần":
        render_cancel_page()
    elif menu == "Tra cứu kết quả đăng ký":
        render_lookup_page()
    elif menu == "Truy vấn phân tán / Thống kê":
        render_distributed_query_page()
    elif menu == "Mô phỏng đồng thời":
        render_concurrency_page()
    elif menu == "Nhật ký thao tác":
        render_log_page()


if __name__ == "__main__":
    main()
