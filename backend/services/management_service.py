"""Service nghiệp vụ quản lý dữ liệu service, gom xử lý trung gian giữa API và tầng database."""

from backend.core.config import SITE_CODES
from backend.db import queries
from backend.db.connections import check_site_connection
from backend.db.distributed_queries import (
    thong_ke_dang_ky_theo_co_so,
    thong_ke_sinh_vien_theo_co_so,
    thong_ke_so_lop_theo_co_so,
)


# Xử lý bước nghiệp vụ tổng quan trong module này.
def dashboard():
    """Xử lý bước nghiệp vụ tổng quan trong module này."""
    students = thong_ke_sinh_vien_theo_co_so()
    classes = thong_ke_so_lop_theo_co_so()
    registrations = thong_ke_dang_ky_theo_co_so()
    return {
        "sites": len(SITE_CODES),
        "students": int(students["so_sinh_vien"].sum()) if not students.empty else 0,
        "class_sections": int(classes["so_lop_mo"].sum()) if not classes.empty else 0,
        "registrations": int(registrations["so_luot_dang_ky"].sum()) if not registrations.empty else 0,
    }


# Xử lý bước nghiệp vụ trạng thái các site trong module này.
def sites_status():
    """Xử lý bước nghiệp vụ trạng thái các site trong module này."""
    rows = []
    for site_code in SITE_CODES:
        ok, message = check_site_connection(site_code)
        rows.append({"site_code": site_code, "status": "OK" if ok else "ERROR", "message": message})
    return rows


# Lấy dữ liệu sinh viên từ nguồn phù hợp để trả về cho tầng gọi phía trên.
def list_students(site_code):
    """Lấy dữ liệu sinh viên từ nguồn phù hợp để trả về cho tầng gọi phía trên."""
    return queries.get_students(site_code)


# Thêm mới dữ liệu sinh viên sau khi nhận thông tin từ form hoặc API.
def add_student(data):
    """Thêm mới dữ liệu sinh viên sau khi nhận thông tin từ form hoặc API."""
    return queries.add_student(data["site_code"], data)


# Lấy dữ liệu giảng viên từ nguồn phù hợp để trả về cho tầng gọi phía trên.
def list_teachers(site_code):
    """Lấy dữ liệu giảng viên từ nguồn phù hợp để trả về cho tầng gọi phía trên."""
    return queries.get_teachers(site_code)


# Thêm mới dữ liệu giảng viên sau khi nhận thông tin từ form hoặc API.
def add_teacher(data):
    """Thêm mới dữ liệu giảng viên sau khi nhận thông tin từ form hoặc API."""
    return queries.add_teacher(data["site_code"], data)


# Lấy dữ liệu học phần từ nguồn phù hợp để trả về cho tầng gọi phía trên.
def list_courses():
    """Lấy dữ liệu học phần từ nguồn phù hợp để trả về cho tầng gọi phía trên."""
    return queries.get_courses("HL")


# Thêm mới dữ liệu học phần sau khi nhận thông tin từ form hoặc API.
def add_course(data):
    """Thêm mới dữ liệu học phần sau khi nhận thông tin từ form hoặc API."""
    return queries.add_course_to_all_sites(data)


# Lấy dữ liệu lớp học phần từ nguồn phù hợp để trả về cho tầng gọi phía trên.
def list_class_sections(site_code):
    """Lấy dữ liệu lớp học phần từ nguồn phù hợp để trả về cho tầng gọi phía trên."""
    return queries.get_class_sections(site_code)


# Thêm mới dữ liệu lớp học phần sau khi nhận thông tin từ form hoặc API.
def add_class_section(data):
    """Thêm mới dữ liệu lớp học phần sau khi nhận thông tin từ form hoặc API."""
    return queries.add_class_section(data["site_code"], data)


# Lấy dữ liệu phòng học từ nguồn phù hợp để trả về cho tầng gọi phía trên.
def list_rooms(site_code):
    """Lấy dữ liệu phòng học từ nguồn phù hợp để trả về cho tầng gọi phía trên."""
    return queries.get_rooms(site_code)


# Thêm mới dữ liệu phòng học sau khi nhận thông tin từ form hoặc API.
def add_room(data):
    """Thêm mới dữ liệu phòng học sau khi nhận thông tin từ form hoặc API."""
    return queries.add_room(data["site_code"], data)


# Lấy dữ liệu lịch học từ nguồn phù hợp để trả về cho tầng gọi phía trên.
def list_schedules(site_code):
    """Lấy dữ liệu lịch học từ nguồn phù hợp để trả về cho tầng gọi phía trên."""
    return queries.get_schedules(site_code)


# Thêm mới dữ liệu lịch học sau khi nhận thông tin từ form hoặc API.
def add_schedule(data):
    """Thêm mới dữ liệu lịch học sau khi nhận thông tin từ form hoặc API."""
    return queries.add_schedule(data["site_code"], data)
