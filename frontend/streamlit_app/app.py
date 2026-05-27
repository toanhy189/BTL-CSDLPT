"""Router chính của frontend Streamlit mới, điều hướng theo vai trò ADMIN, SINH_VIEN và GIANG_VIEN."""

import streamlit as st

from styles import (
    load_styles,
    render_header,
    render_sidebar_brand,
    render_support_box,
    role_portal,
)
from ui_pages.admin.admin_concurrency_page import render_admin_concurrency
from ui_pages.admin.admin_dashboard_page import render_admin_dashboard
from ui_pages.admin.admin_distributed_query_page import render_admin_distributed_query
from ui_pages.admin.admin_log_page import render_admin_log
from ui_pages.admin.admin_management_page import render_admin_management
from ui_pages.login_page import render_login_page
from ui_pages.student.student_cancel_page import render_student_cancel
from ui_pages.student.student_home_page import render_student_home
from ui_pages.student.student_lookup_page import render_student_lookup
from ui_pages.student.student_profile_page import render_student_profile
from ui_pages.student.student_registration_page import render_student_registration
from ui_pages.student.student_schedule_page import render_student_schedule
from ui_pages.teacher.teacher_classes_page import render_teacher_classes
from ui_pages.teacher.teacher_home_page import render_teacher_home
from ui_pages.teacher.teacher_schedule_page import render_teacher_schedule
from ui_pages.teacher.teacher_stats_page import render_teacher_stats
from ui_pages.teacher.teacher_students_page import render_teacher_students


st.set_page_config(
    page_title="Hệ thống đăng ký học phần nhiều cơ sở",
    page_icon="📘",
    layout="wide",
)


# Menu được tách theo vai trò để người dùng chỉ thấy đúng nghiệp vụ được phép.
ADMIN_MENU = [
    "Tổng quan",
    "Quản lý dữ liệu",
    "Truy vấn phân tán / Thống kê",
    "Mô phỏng đồng thời",
    "Nhật ký thao tác",
]

STUDENT_MENU = [
    "Trang chủ",
    "Hồ sơ cá nhân",
    "Đăng ký học phần",
    "Hủy đăng ký",
    "Kết quả đăng ký",
    "Thời khóa biểu",
]

TEACHER_MENU = [
    "Trang chủ",
    "Lớp học phần phụ trách",
    "Danh sách sinh viên",
    "Lịch dạy",
    "Thống kê lớp",
]

MENU_ICONS = {
    "Trang chủ": "⌂",
    "Hồ sơ cá nhân": "○",
    "Đăng ký học phần": "▤",
    "Hủy đăng ký": "⊖",
    "Kết quả đăng ký": "▣",
    "Thời khóa biểu": "▦",
    "Tổng quan": "⌂",
    "Quản lý dữ liệu": "▥",
    "Truy vấn phân tán / Thống kê": "▧",
    "Mô phỏng đồng thời": "⇄",
    "Nhật ký thao tác": "☰",
    "Lớp học phần phụ trách": "▤",
    "Danh sách sinh viên": "◌",
    "Lịch dạy": "▦",
    "Thống kê lớp": "▥",
}


# Xóa token và thông tin user khỏi session rồi tải lại ứng dụng.
def logout() -> None:
    """Xóa token và thông tin user khỏi session rồi tải lại ứng dụng."""
    st.session_state.pop("access_token", None)
    st.session_state.pop("user", None)
    st.rerun()


# Chọn danh sách menu phù hợp với vai trò đăng nhập của người dùng.
def _menu_for_role(role: str) -> list[str]:
    """Chọn danh sách menu phù hợp với vai trò đăng nhập của người dùng."""
    if role == "ADMIN":
        return ADMIN_MENU
    if role == "GIANG_VIEN":
        return TEACHER_MENU
    return STUDENT_MENU


# Vẽ sidebar theo vai trò để người dùng chỉ thấy các nghiệp vụ được phép.
def render_role_sidebar(user: dict) -> str:
    """Vẽ sidebar theo vai trò để người dùng chỉ thấy các nghiệp vụ được phép."""
    role = user["role"]
    menu = _menu_for_role(role)
    render_sidebar_brand(role_portal(user))

    if role == "ADMIN":
        st.sidebar.markdown('<div class="sidebar-group">Quản trị hệ thống</div>', unsafe_allow_html=True)
    elif role == "GIANG_VIEN":
        st.sidebar.markdown('<div class="sidebar-group">Cổng giảng viên</div>', unsafe_allow_html=True)
    else:
        st.sidebar.markdown('<div class="sidebar-group">Cổng sinh viên</div>', unsafe_allow_html=True)

    selected = st.sidebar.radio(
        "Menu",
        menu,
        key=f"nav_{role}",
        label_visibility="collapsed",
        format_func=lambda item: f"{MENU_ICONS.get(item, '•')}  {item}",
    )
    st.sidebar.divider()
    if st.sidebar.button("Đăng xuất"):
        logout()
    render_support_box(role)
    return selected


# Điều hướng các trang nghiệp vụ dành cho quản trị viên.
def render_admin(menu: str, token: str) -> None:
    """Điều hướng các trang nghiệp vụ dành cho quản trị viên."""
    if menu == "Tổng quan":
        render_admin_dashboard(token)
    elif menu == "Quản lý dữ liệu":
        render_admin_management(token)
    elif menu == "Truy vấn phân tán / Thống kê":
        render_admin_distributed_query(token)
    elif menu == "Mô phỏng đồng thời":
        render_admin_concurrency(token)
    elif menu == "Nhật ký thao tác":
        render_admin_log(token)


# Điều hướng các trang nghiệp vụ dành cho sinh viên.
def render_student(menu: str, token: str, user: dict) -> None:
    """Điều hướng các trang nghiệp vụ dành cho sinh viên."""
    if menu == "Trang chủ":
        render_student_home(user)
    elif menu == "Hồ sơ cá nhân":
        render_student_profile(token)
    elif menu == "Đăng ký học phần":
        render_student_registration(token, user)
    elif menu == "Hủy đăng ký":
        render_student_cancel(token, user)
    elif menu == "Kết quả đăng ký":
        render_student_lookup(token)
    elif menu == "Thời khóa biểu":
        render_student_schedule(token)


# Điều hướng các trang nghiệp vụ dành cho giảng viên.
def render_teacher(menu: str, token: str) -> None:
    """Điều hướng các trang nghiệp vụ dành cho giảng viên."""
    if menu == "Trang chủ":
        render_teacher_home(token)
    elif menu == "Lớp học phần phụ trách":
        render_teacher_classes(token)
    elif menu == "Danh sách sinh viên":
        render_teacher_students(token)
    elif menu == "Lịch dạy":
        render_teacher_schedule(token)
    elif menu == "Thống kê lớp":
        render_teacher_stats(token)


# Điểm vào của module, chuẩn bị dữ liệu/giao diện rồi điều phối sang luồng nghiệp vụ phù hợp.
def main() -> None:
    """Điểm vào của module, chuẩn bị dữ liệu/giao diện rồi điều phối sang luồng nghiệp vụ phù hợp."""
    load_styles()
    token = st.session_state.get("access_token")
    user = st.session_state.get("user")

    # Chưa có phiên đăng nhập thì dừng luồng chính và hiển thị form đăng nhập.
    if not token or not user:
        render_login_page()
        return

    render_header(user, subtitle=role_portal(user))
    menu = render_role_sidebar(user)

    # Sau khi đăng nhập, vai trò quyết định nhóm trang nghiệp vụ được render.
    if user["role"] == "ADMIN":
        render_admin(menu, token)
    elif user["role"] == "GIANG_VIEN":
        render_teacher(menu, token)
    elif user["role"] == "SINH_VIEN":
        render_student(menu, token, user)
    else:
        st.error("Role không hợp lệ")


if __name__ == "__main__":
    main()
