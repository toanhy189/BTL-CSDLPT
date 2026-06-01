"""Router FastAPI cho nhóm nghiệp vụ registration api, nhận request và chuyển xuống service phù hợp."""

from fastapi import APIRouter, Depends, Query

from backend.core.security import require_role
from backend.db import queries
from backend.db.queries import df_to_records
from backend.models.schemas import CancelRequest, RegisterRequest
from backend.services.registration_service import cancel_registration, register_course


router = APIRouter(prefix="/student", tags=["student"])


# Xử lý bước nghiệp vụ đăng ký trong module này.
@router.post("/register")
def register(payload: RegisterRequest, current_user=Depends(require_role(["SINH_VIEN", "ADMIN"]))):
    """Xử lý bước nghiệp vụ đăng ký trong module này."""
    student_id = payload.student_id
    student_headquarter = payload.student_headquarter
    if current_user["role"] == "SINH_VIEN":
        student_id = current_user["ref_id"]
        student_headquarter = current_user["id_headquarter"]
    success, message = register_course(
        student_id,
        student_headquarter,
        payload.class_site_code,
        payload.class_id,
    )
    return {"success": success, "message": message}


# Xử lý bước nghiệp vụ hủy đăng ký trong module này.
@router.post("/cancel")
def cancel(payload: CancelRequest, current_user=Depends(require_role(["SINH_VIEN", "ADMIN"]))):
    student_id = payload.student_id
    if current_user["role"] == "SINH_VIEN":
        student_id = current_user["ref_id"]
    success, message = cancel_registration(student_id, payload.class_site_code, payload.class_id)
    return {"success": success, "message": message}


# Xử lý bước nghiệp vụ registrations trong module này.
@router.get("/registrations")
def registrations(current_user=Depends(require_role(["SINH_VIEN", "ADMIN"])), student_id: str | None = None):
    lookup_id = student_id or current_user["ref_id"]
    return df_to_records(queries.get_registration_by_student(lookup_id))


# Xử lý bước nghiệp vụ open classes trong module này.
@router.get("/open-classes")
def open_classes(site_code: str = Query("HL"), current_user=Depends(require_role(["SINH_VIEN", "ADMIN"]))):
    if current_user["role"] == "SINH_VIEN":
        return df_to_records(
            queries.get_open_class_sections_for_student(
                site_code,
                current_user["ref_id"],
                current_user["id_headquarter"],
            )
        )
    return df_to_records(queries.get_class_sections(site_code))


# Xử lý bước nghiệp vụ lịch học trong module này.
@router.get("/schedule")
def schedule(
    current_user=Depends(require_role(["SINH_VIEN", "ADMIN"])),
    student_id: str | None = None,
    semester: int | None = Query(None),
    school_year: int | None = Query(None),
    week_number: int | None = Query(None),
):
    lookup_id = student_id or current_user["ref_id"]
    return df_to_records(queries.get_student_schedule(lookup_id, semester, school_year, week_number))
