"""Bộ định tuyến FastAPI dành cho quản trị viên, nhận yêu cầu quản lý dữ liệu và chuyển xuống service phù hợp."""

from fastapi import APIRouter, Depends, Query

from backend.core.registration_config import get_registration_config, set_registration_open
from backend.core.security import require_role
from backend.db.queries import df_to_records
from backend.models.schemas import (
    ClassSectionCreate,
    CourseCreate,
    RegistrationPeriodStatusUpdate,
    RegistrationStatusUpdate,
    RegistrationPeriodCreate,
    RoomCreate,
    ScheduleCreate,
    StudentCreate,
    TeacherCreate,
    TrainingProgramCreate,
)
from backend.services import management_service


router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_role(["ADMIN"]))])


# Xử lý bước nghiệp vụ tổng quan trong module này.
@router.get("/dashboard")
def dashboard():
    return management_service.dashboard()


# Xử lý bước nghiệp vụ trạng thái các site trong module này.
@router.get("/sites/status")
def sites_status():
    return management_service.sites_status()


@router.get("/offline-operations")
def offline_operations(status: str | None = Query(None)):
    return management_service.list_offline_operations(status)


@router.post("/offline-operations/retry-all")
def retry_all_offline_operations():
    return management_service.retry_all_offline_operations()


@router.post("/offline-operations/{operation_id}/retry")
def retry_offline_operation(operation_id: int):
    success, message = management_service.retry_offline_operation(operation_id)
    return {"success": success, "message": message}


@router.post("/offline-operations/{operation_id}/cancel")
def cancel_offline_operation(operation_id: int):
    success, message = management_service.cancel_offline_operation(operation_id)
    return {"success": success, "message": message}


@router.get("/registration-status")
def registration_status():
    """Trả về trạng thái mở/đóng đăng ký học phần."""
    return get_registration_config()


@router.post("/registration-status")
def update_registration_status(payload: RegistrationStatusUpdate):
    """Quản trị viên cập nhật trạng thái mở/đóng đăng ký học phần."""
    return set_registration_open(payload.registration_open)


# Xử lý bước nghiệp vụ sinh viên trong module này.
@router.get("/students")
def students(site_code: str = Query("HL")):
    return df_to_records(management_service.list_students(site_code))


# Thêm mới dữ liệu sinh viên sau khi nhận thông tin từ form hoặc API.
@router.post("/students")
def add_student(payload: StudentCreate):
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
    return df_to_records(management_service.list_teachers(site_code))


# Thêm mới dữ liệu giảng viên sau khi nhận thông tin từ form hoặc API.
@router.post("/teachers")
def add_teacher(payload: TeacherCreate):
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
    return df_to_records(management_service.list_courses())


# Thêm mới dữ liệu học phần sau khi nhận thông tin từ form hoặc API.
@router.post("/courses")
def add_course(payload: CourseCreate):
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


@router.get("/training-programs")
def training_programs():
    return df_to_records(management_service.list_training_programs())


@router.post("/training-programs")
def add_training_program(payload: TrainingProgramCreate):
    success, message = management_service.add_training_program(payload.dict())
    return {"success": success, "message": message}


@router.put("/training-programs/{department_id}/{subject_id}")
def update_training_program(department_id: str, subject_id: str, payload: TrainingProgramCreate):
    success, message = management_service.update_training_program(department_id, subject_id, payload.dict())
    return {"success": success, "message": message}


@router.delete("/training-programs/{department_id}/{subject_id}")
def delete_training_program(department_id: str, subject_id: str):
    success, message = management_service.delete_training_program(department_id, subject_id)
    return {"success": success, "message": message}


@router.get("/registration-periods")
def registration_periods():
    return df_to_records(management_service.list_registration_periods())


@router.post("/registration-periods")
def add_registration_period(payload: RegistrationPeriodCreate):
    success, message = management_service.add_registration_period(payload.dict())
    return {"success": success, "message": message}


@router.put("/registration-periods/{period_id}")
def update_registration_period(period_id: str, payload: RegistrationPeriodCreate):
    success, message = management_service.update_registration_period(period_id, payload.dict())
    return {"success": success, "message": message}


@router.patch("/registration-periods/{period_id}/status")
def update_registration_period_status(period_id: str, payload: RegistrationPeriodStatusUpdate):
    success, message = management_service.update_registration_period_status(period_id, payload.is_open)
    return {"success": success, "message": message}


@router.delete("/registration-periods/{period_id}")
def delete_registration_period(period_id: str):
    success, message = management_service.delete_registration_period(period_id)
    return {"success": success, "message": message}


# Xử lý bước nghiệp vụ lớp học phần trong module này.
@router.get("/class-sections")
def class_sections(site_code: str = Query("HL")):
    return df_to_records(management_service.list_class_sections(site_code))


# Thêm mới dữ liệu lớp học phần sau khi nhận thông tin từ form hoặc API.
@router.post("/class-sections")
def add_class_section(payload: ClassSectionCreate):
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
    return df_to_records(management_service.list_rooms(site_code))


# Thêm mới dữ liệu phòng học sau khi nhận thông tin từ form hoặc API.
@router.post("/rooms")
def add_room(payload: RoomCreate):
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
    return df_to_records(management_service.list_schedules(site_code))


# Thêm mới dữ liệu lịch học sau khi nhận thông tin từ form hoặc API.
@router.post("/schedules")
def add_schedule(payload: ScheduleCreate):
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
