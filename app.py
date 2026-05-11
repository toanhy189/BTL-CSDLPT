"""Router chinh cua ung dung Streamlit."""

import streamlit as st

from pages.cancel_page import render_cancel_page
from pages.concurrency_page import render_concurrency_page
from pages.dashboard_page import render_dashboard_page
from pages.distributed_query_page import render_distributed_query_page
from pages.log_page import render_log_page
from pages.lookup_page import render_lookup_page
from pages.management_page import render_management_page
from pages.registration_page import render_registration_page


st.set_page_config(
    page_title="Hệ thống đăng ký học phần nhiều cơ sở",
    page_icon="🎓",
    layout="wide",
)


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


def main():
    st.sidebar.title("CSDL phân tán")
    menu = st.sidebar.radio("Chức năng", MENU)

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
