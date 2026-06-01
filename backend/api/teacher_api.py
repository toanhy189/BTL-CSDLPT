"""Router FastAPI cho nhóm nghiệp vụ giảng viên api, nhận request và chuyển xuống service phù hợp."""

from fastapi import APIRouter, Depends, Query

from backend.core.security import require_role
from backend.db import queries
from backend.db.queries import df_to_records


router = APIRouter(prefix="/teacher", tags=["teacher"], dependencies=[Depends(require_role(["GIANG_VIEN"]))])


# Xử lý bước nghiệp vụ classes trong module này.
@router.get("/classes")
def classes(current_user=Depends(require_role(["GIANG_VIEN"]))):
    return df_to_records(queries.get_teacher_classes(current_user["ref_id"], current_user["id_headquarter"]))


# Xử lý bước nghiệp vụ sinh viên trong lớp trong module này.
@router.get("/classes/{class_id}/students")
def class_students(class_id: str, current_user=Depends(require_role(["GIANG_VIEN"]))):
    return df_to_records(queries.get_registration_by_class(current_user["id_headquarter"], class_id))


# Xử lý bước nghiệp vụ lịch học trong module này.
@router.get("/schedule")
def schedule(
    current_user=Depends(require_role(["GIANG_VIEN"])),
    semester: int | None = Query(None),
    school_year: int | None = Query(None),
    week_number: int | None = Query(None),
):
    return df_to_records(
        queries.get_teacher_schedule(current_user["ref_id"], current_user["id_headquarter"], semester, school_year, week_number)
    )


# Xử lý bước nghiệp vụ statistics trong module này.
@router.get("/statistics")
def statistics(current_user=Depends(require_role(["GIANG_VIEN"]))):
    classes_df = queries.get_teacher_classes(current_user["ref_id"], current_user["id_headquarter"])
    total_students = int(classes_df["number_of_student"].sum()) if not classes_df.empty else 0
    return {
        "class_count": len(classes_df),
        "total_students": total_students,
        "site": current_user["id_headquarter"],
    }
