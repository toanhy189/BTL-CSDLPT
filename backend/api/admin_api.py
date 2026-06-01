"""Router FastAPI dành cho quản trị viên, nhận request quản lý dữ liệu và chuyển xuống service phù hợp."""

from fastapi import APIRouter, Depends, Query

from backend.core.registration_config import get_registration_config, set_registration_open
from backend.core.security import require_role
from backend.db.queries import df_to_records
from backend.models.schemas import (
    ClassSectionCreate,
    CourseCreate,
    RegistrationStatusUpdate,
    RoomCreate,
    ScheduleCreate,
    StudentCreate,
    TeacherCreate,
)
from backend.services import management_service


router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_role(["ADMIN"]))])


# Xử lý bước nghiệp vụ tổng quan trong module này.
@router.get("/dashboard")
def dashboard():
    """Xử lý bước nghiệp vụ tổng quan trong module này."""
    return management_service.dashboard()


# Xử lý bước nghiệp vụ trạng thái các site trong module này.
@router.get("/sites/status")
def sites_status():
    """Xử lý bước nghiệp vụ trạng thái các site trong module này."""
    return management_service.sites_status()


@router.get("/registration-status")
def registration_status():
    """Tra ve trang thai mo/dong dang ky hoc phan."""
    return get_registration_config()


@router.post("/registration-status")
def update_registration_status(payload: RegistrationStatusUpdate):
    """Admin cap nhat trang thai mo/dong dang ky hoc phan."""
    return set_registration_open(payload.registration_open)


# Xử lý bước nghiệp vụ sinh viên trong module này.
@router.get("/students")
def students(site_code: str = Query("HL")):
    """Xử lý bước nghiệp vụ sinh viên trong module này."""
    return df_to_records(management_service.list_students(site_code))


# Thêm mới dữ liệu sinh viên sau khi nhận thông tin từ form hoặc API.
@router.post("/students")
def add_student(payload: StudentCreate):
    """Thêm mới dữ liệu sinh viên sau khi nhận thông tin từ form hoặc API."""
    success, message = management_service.add_student(payload.dict())
    return {"success": success, "message": message}


@router.put("/students/{student_id}")
def update_student(student_id: str, payload: StudentCreate):
    success, message = management_service.update_student(student_id, payload.dict())
    return {"success": success, "message": message}


@router.delete("/students/{student_id}")
def delete_student(student_id: str, site_code: str = Query("HL")):
    success, message = management_service.delete_student(site_code, student_id)
    return {"success": success, "message": message}


# Xử lý bước nghiệp vụ giảng viên trong module này.
@router.get("/teachers")
def teachers(site_code: str = Query("HL")):
    """Xử lý bước nghiệp vụ giảng viên trong module này."""
    return df_to_records(management_service.list_teachers(site_code))


# Thêm mới dữ liệu giảng viên sau khi nhận thông tin từ form hoặc API.
@router.post("/teachers")
def add_teacher(payload: TeacherCreate):
    """Thêm mới dữ liệu giảng viên sau khi nhận thông tin từ form hoặc API."""
    success, message = management_service.add_teacher(payload.dict())
    return {"success": success, "message": message}


@router.put("/teachers/{teacher_id}")
def update_teacher(teacher_id: str, payload: TeacherCreate):
    success, message = management_service.update_teacher(teacher_id, payload.dict())
    return {"success": success, "message": message}


@router.delete("/teachers/{teacher_id}")
def delete_teacher(teacher_id: str, site_code: str = Query("HL")):
    success, message = management_service.delete_teacher(site_code, teacher_id)
    return {"success": success, "message": message}


# Xử lý bước nghiệp vụ học phần trong module này.
@router.get("/courses")
def courses():
    """Xử lý bước nghiệp vụ học phần trong module này."""
    return df_to_records(management_service.list_courses())


# Thêm mới dữ liệu học phần sau khi nhận thông tin từ form hoặc API.
@router.post("/courses")
def add_course(payload: CourseCreate):
    """Thêm mới dữ liệu học phần sau khi nhận thông tin từ form hoặc API."""
    success, message = management_service.add_course(payload.dict())
    return {"success": success, "message": message}


@router.put("/courses/{course_id}")
def update_course(course_id: str, payload: CourseCreate):
    success, message = management_service.update_course(course_id, payload.dict())
    return {"success": success, "message": message}


@router.delete("/courses/{course_id}")
def delete_course(course_id: str):
    success, message = management_service.delete_course(course_id)
    return {"success": success, "message": message}


# Xử lý bước nghiệp vụ lớp học phần trong module này.
@router.get("/class-sections")
def class_sections(site_code: str = Query("HL")):
    """Xử lý bước nghiệp vụ lớp học phần trong module này."""
    return df_to_records(management_service.list_class_sections(site_code))


# Thêm mới dữ liệu lớp học phần sau khi nhận thông tin từ form hoặc API.
@router.post("/class-sections")
def add_class_section(payload: ClassSectionCreate):
    """Thêm mới dữ liệu lớp học phần sau khi nhận thông tin từ form hoặc API."""
    success, message = management_service.add_class_section(payload.dict())
    return {"success": success, "message": message}


@router.put("/class-sections/{class_id}")
def update_class_section(class_id: str, payload: ClassSectionCreate):
    success, message = management_service.update_class_section(class_id, payload.dict())
    return {"success": success, "message": message}


@router.delete("/class-sections/{class_id}")
def delete_class_section(class_id: str, site_code: str = Query("HL")):
    success, message = management_service.delete_class_section(site_code, class_id)
    return {"success": success, "message": message}


# Xử lý bước nghiệp vụ phòng học trong module này.
@router.get("/rooms")
def rooms(site_code: str = Query("HL")):
    """Xử lý bước nghiệp vụ phòng học trong module này."""
    return df_to_records(management_service.list_rooms(site_code))


# Thêm mới dữ liệu phòng học sau khi nhận thông tin từ form hoặc API.
@router.post("/rooms")
def add_room(payload: RoomCreate):
    """Thêm mới dữ liệu phòng học sau khi nhận thông tin từ form hoặc API."""
    success, message = management_service.add_room(payload.dict())
    return {"success": success, "message": message}


@router.put("/rooms/{room_id}")
def update_room(room_id: str, payload: RoomCreate):
    success, message = management_service.update_room(room_id, payload.dict())
    return {"success": success, "message": message}


@router.delete("/rooms/{room_id}")
def delete_room(room_id: str, site_code: str = Query("HL")):
    success, message = management_service.delete_room(site_code, room_id)
    return {"success": success, "message": message}


# Xử lý bước nghiệp vụ lịch học trong module này.
@router.get("/schedules")
def schedules(site_code: str = Query("HL")):
    """Xử lý bước nghiệp vụ lịch học trong module này."""
    return df_to_records(management_service.list_schedules(site_code))


# Thêm mới dữ liệu lịch học sau khi nhận thông tin từ form hoặc API.
@router.post("/schedules")
def add_schedule(payload: ScheduleCreate):
    """Thêm mới dữ liệu lịch học sau khi nhận thông tin từ form hoặc API."""
    success, message = management_service.add_schedule(payload.dict())
    return {"success": success, "message": message}


@router.put("/schedules/{schedule_id}")
def update_schedule(schedule_id: str, payload: ScheduleCreate):
    success, message = management_service.update_schedule(schedule_id, payload.dict())
    return {"success": success, "message": message}


@router.delete("/schedules/{schedule_id}")
def delete_schedule(schedule_id: str, site_code: str = Query("HL")):
    success, message = management_service.delete_schedule(site_code, schedule_id)
    return {"success": success, "message": message}
