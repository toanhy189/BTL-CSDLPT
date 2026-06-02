"""Bộ định tuyến giao diện Streamlit cho hệ thống đăng ký học phần phân tán."""

import streamlit as st

from styles import load_styles, render_header, render_sidebar_brand, render_support_box, role_portal
from ui_pages.admin.admin_concurrency_page import render_admin_concurrency
from ui_pages.admin.admin_dashboard_page import render_admin_dashboard
from ui_pages.admin.admin_distributed_query_page import render_admin_distributed_query
from ui_pages.admin.admin_log_page import render_admin_log
from ui_pages.admin.admin_management_page import render_admin_management
from ui_pages.admin.admin_offline_operations_page import render_admin_offline_operations
from ui_pages.login_page import render_login_page
from ui_pages.student.student_cancel_page import render_student_cancel
from ui_pages.student.student_home_page import render_student_home
from ui_pages.student.student_profile_page import render_student_profile
from ui_pages.student.student_registration_page import render_student_registration
from ui_pages.student.student_schedule_page import render_student_schedule
from ui_pages.teacher.teacher_classes_page import render_teacher_classes
from ui_pages.teacher.teacher_home_page import render_teacher_home
from ui_pages.teacher.teacher_schedule_page import render_teacher_schedule
from ui_pages.teacher.teacher_students_page import render_teacher_students


st.set_page_config(
    page_title="Hệ thống đăng ký học phần nhiều cơ sở",
    layout="wide",
    initial_sidebar_state="expanded",
)


ADMIN_MENU = [
    "Tổng quan",
    "Quản lý dữ liệu",
    "Truy vấn phân tán",
    "Yêu cầu chờ xử lý",
    "Mô phỏng đồng thời",
    "Nhật ký thao tác",
]

STUDENT_MENU = [
    "Trang chủ",
    "Hồ sơ cá nhân",
    "Đăng ký học phần",
    "Hủy đăng ký",
    "Thời khóa biểu",
]

TEACHER_MENU = [
    "Trang chủ",
    "Lớp học phần phụ trách",
    "Danh sách sinh viên",
    "Lịch dạy",
]

MENU_ICONS = {
    "Trang chủ": "Trang chủ",
    "Hồ sơ cá nhân": "Hồ sơ",
    "Đăng ký học phần": "Đăng ký",
    "Hủy đăng ký": "Hủy",
    "Thời khóa biểu": "TKB",
    "Tổng quan": "Tổng quan",
    "Quản lý dữ liệu": "Quản lý",
    "Truy vấn phân tán": "Phân tán",
    "Yêu cầu chờ xử lý": "Chờ xử lý",
    "Mô phỏng đồng thời": "Đồng thời",
    "Nhật ký thao tác": "Nhật ký",
    "Lớp học phần phụ trách": "Lớp",
    "Danh sách sinh viên": "Sinh viên",
    "Lịch dạy": "Lịch dạy",
}


def logout() -> None:
    st.session_state.pop("access_token", None)
    st.session_state.pop("user", None)
    st.rerun()


def _menu_for_role(role: str) -> list[str]:
    if role == "ADMIN":
        return ADMIN_MENU
    if role == "GIANG_VIEN":
        return TEACHER_MENU
    return STUDENT_MENU


def render_role_sidebar(user: dict) -> str:
    role = user["role"]
    menu = _menu_for_role(role)
    render_sidebar_brand(role_portal(user))

    group_name = {
        "ADMIN": "Quản trị hệ thống",
        "GIANG_VIEN": "Cổng giảng viên",
        "SINH_VIEN": "Cổng sinh viên",
    }.get(role, "Menu")
    st.sidebar.markdown(f'<div class="sidebar-group">{group_name}</div>', unsafe_allow_html=True)

    selected = st.sidebar.radio(
        "Menu",
        menu,
        key=f"nav_{role}",
        label_visibility="collapsed",
        format_func=lambda item: f"{MENU_ICONS.get(item, 'Menu')} - {item}",
    )
    st.sidebar.divider()
    if st.sidebar.button("Đăng xuất"):
        logout()
    render_support_box(role)
    return selected


def render_admin(menu: str, token: str) -> None:
    if menu == "Tổng quan":
        render_admin_dashboard(token)
    elif menu == "Quản lý dữ liệu":
        render_admin_management(token)
    elif menu == "Truy vấn phân tán":
        render_admin_distributed_query(token)
    elif menu == "Yêu cầu chờ xử lý":
        render_admin_offline_operations(token)
    elif menu == "Mô phỏng đồng thời":
        render_admin_concurrency(token)
    elif menu == "Nhật ký thao tác":
        render_admin_log(token)


def render_student(menu: str, token: str, user: dict) -> None:
    if menu == "Trang chủ":
        render_student_home(token, user)
    elif menu == "Hồ sơ cá nhân":
        render_student_profile(token)
    elif menu == "Đăng ký học phần":
        render_student_registration(token, user)
    elif menu == "Hủy đăng ký":
        render_student_cancel(token, user)
    elif menu == "Thời khóa biểu":
        render_student_schedule(token)


def render_teacher(menu: str, token: str) -> None:
    if menu == "Trang chủ":
        render_teacher_home(token)
    elif menu == "Lớp học phần phụ trách":
        render_teacher_classes(token)
    elif menu == "Danh sách sinh viên":
        render_teacher_students(token)
    elif menu == "Lịch dạy":
        render_teacher_schedule(token)


def main() -> None:
    load_styles()
    token = st.session_state.get("access_token")
    user = st.session_state.get("user")

    if not token or not user:
        render_login_page()
        return

    render_header(user, subtitle=role_portal(user))
    menu = render_role_sidebar(user)

    if user["role"] == "ADMIN":
        render_admin(menu, token)
    elif user["role"] == "GIANG_VIEN":
        render_teacher(menu, token)
    elif user["role"] == "SINH_VIEN":
        render_student(menu, token, user)
    else:
        st.error("Vai trò không hợp lệ")


if __name__ == "__main__":
    main()
