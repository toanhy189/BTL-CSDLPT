"""Service nghiệp vụ quản lý dữ liệu service, gom xử lý trung gian giữa API và tầng database."""

from backend.core.config import SITE_CODES
from backend.db import queries
from backend.db.connections import check_site_connection
from backend.db.distributed_queries import (
    thong_ke_dang_ky_theo_co_so,
    thong_ke_sinh_vien_theo_co_so,
    thong_ke_so_lop_theo_co_so,
)
from backend.services.offline_operation_service import (
    list_offline_operations as _list_offline_operations,
    retry_all_pending_operations as _retry_all_pending_operations,
    retry_offline_operation as _retry_offline_operation,
    update_offline_operation_status,
)


# Xử lý bước nghiệp vụ tổng quan trong module này.
def dashboard():
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
    rows = []
    for site_code in SITE_CODES:
        ok, message = check_site_connection(site_code)
        rows.append({"site_code": site_code, "status": "OK" if ok else "ERROR", "message": message})
    return rows


def list_offline_operations(status=None):
    return _list_offline_operations(status)


def retry_offline_operation(operation_id):
    return _retry_offline_operation(operation_id)


def retry_all_offline_operations():
    return _retry_all_pending_operations()


def cancel_offline_operation(operation_id):
    return update_offline_operation_status(operation_id, "CANCELLED", "Admin cancelled offline operation")


# Lấy dữ liệu sinh viên từ nguồn phù hợp để trả về cho tầng gọi phía trên.
def list_students(site_code):
    return queries.get_students(site_code)


# Thêm mới dữ liệu sinh viên sau khi nhận thông tin từ form hoặc API.
def add_student(data):
    return queries.add_student(data["site_code"], data)


def update_student(student_id, data):
    return queries.update_student(data["site_code"], student_id, data)


def delete_student(site_code, student_id):
    return queries.delete_student(site_code, student_id)


# Lấy dữ liệu giảng viên từ nguồn phù hợp để trả về cho tầng gọi phía trên.
def list_teachers(site_code):
    return queries.get_teachers(site_code)


# Thêm mới dữ liệu giảng viên sau khi nhận thông tin từ form hoặc API.
def add_teacher(data):
    return queries.add_teacher(data["site_code"], data)


def update_teacher(teacher_id, data):
    return queries.update_teacher(data["site_code"], teacher_id, data)


def delete_teacher(site_code, teacher_id):
    return queries.delete_teacher(site_code, teacher_id)


# Lấy dữ liệu học phần từ nguồn phù hợp để trả về cho tầng gọi phía trên.
def list_courses():
    return queries.get_courses("HL")


# Thêm mới dữ liệu học phần sau khi nhận thông tin từ form hoặc API.
def add_course(data):
    return queries.add_course_to_all_sites(data)


def update_course(course_id, data):
    return queries.update_course_all_sites(course_id, data)


def delete_course(course_id):
    return queries.delete_course_all_sites(course_id)


def list_training_programs():
    return queries.get_training_programs("HL")


def add_training_program(data):
    return queries.add_training_program_to_all_sites(data)


def update_training_program(department_id, subject_id, data):
    return queries.update_training_program_all_sites(department_id, subject_id, data)


def delete_training_program(department_id, subject_id):
    return queries.delete_training_program_all_sites(department_id, subject_id)


def list_registration_periods():
    return queries.get_registration_periods("HL")


def add_registration_period(data):
    return queries.add_registration_period_to_all_sites(data)


def update_registration_period(period_id, data):
    return queries.update_registration_period_all_sites(period_id, data)


def update_registration_period_status(period_id, is_open):
    return queries.update_registration_period_status_all_sites(period_id, is_open)


def delete_registration_period(period_id):
    return queries.delete_registration_period_all_sites(period_id)


# Lấy dữ liệu lớp học phần từ nguồn phù hợp để trả về cho tầng gọi phía trên.
def list_class_sections(site_code):
    return queries.get_class_sections(site_code)


# Thêm mới dữ liệu lớp học phần sau khi nhận thông tin từ form hoặc API.
def add_class_section(data):
    return queries.add_class_section(data["site_code"], data)


def update_class_section(class_id, data):
    return queries.update_class_section(data["site_code"], class_id, data)


def delete_class_section(site_code, class_id):
    return queries.delete_class_section(site_code, class_id)


# Lấy dữ liệu phòng học từ nguồn phù hợp để trả về cho tầng gọi phía trên.
def list_rooms(site_code):
    return queries.get_rooms(site_code)


# Thêm mới dữ liệu phòng học sau khi nhận thông tin từ form hoặc API.
def add_room(data):
    return queries.add_room(data["site_code"], data)


def update_room(room_id, data):
    return queries.update_room(data["site_code"], room_id, data)


def delete_room(site_code, room_id):
    return queries.delete_room(site_code, room_id)


# Lấy dữ liệu lịch học từ nguồn phù hợp để trả về cho tầng gọi phía trên.
def list_schedules(site_code):
    return queries.get_schedules(site_code)


# Thêm mới dữ liệu lịch học sau khi nhận thông tin từ form hoặc API.
def add_schedule(data):
    return queries.add_schedule(data["site_code"], data)


def update_schedule(schedule_id, data):
    return queries.update_schedule(data["site_code"], schedule_id, data)


def delete_schedule(site_code, schedule_id):
    return queries.delete_schedule(site_code, schedule_id)
