"""Router FastAPI cho nhóm nghiệp vụ concurrency api, nhận request và chuyển xuống service phù hợp."""

from fastapi import APIRouter, Depends, Query

from backend.core.security import require_role
from backend.db.queries import df_to_records
from backend.models.schemas import ConcurrentRegistrationRequest
from backend.services.log_service import read_logs, write_log
from backend.services.registration_service import reset_test_class, simulate_concurrent_registration


router = APIRouter(prefix="/concurrency", tags=["concurrency"], dependencies=[Depends(require_role(["ADMIN"]))])


# Xử lý bước nghiệp vụ simulate trong module này.
@router.post("/simulate-registration")
def simulate(payload: ConcurrentRegistrationRequest):
    """Xử lý bước nghiệp vụ simulate trong module này."""
    df = simulate_concurrent_registration(
        payload.class_site_code,
        payload.class_id,
        [item.dict() for item in payload.students],
    )
    success_count = int(df["success"].sum()) if not df.empty else 0
    total = len(df)
    fail_count = total - success_count
    write_log(f"MO_PHONG_DONG_THOI class={payload.class_id} success={success_count}/{total}")
    return {
        "success": True,
        "total": total,
        "success_count": success_count,
        "fail_count": fail_count,
        "data": df_to_records(df),
    }


# Reset lop test de demo dong thoi lap lai duoc trong Swagger hoac Streamlit.
@router.post("/reset-test-class")
def reset_test(
    class_site_code: str = Query("HL"),
    class_id: str = Query("LHP-HL-TEST"),
    max_student: int = Query(1, ge=1),
):
    """Reset lop test de demo dong thoi lap lai duoc trong Swagger hoac Streamlit."""
    success, message = reset_test_class(class_site_code, class_id, max_student)
    return {
        "success": success,
        "message": message,
        "class_site_code": class_site_code,
        "class_id": class_id,
        "max_student": max_student,
    }


# Xử lý bước nghiệp vụ nhật ký trong module này.
@router.get("/logs")
def logs():
    """Xử lý bước nghiệp vụ nhật ký trong module này."""
    return {"logs": read_logs(limit=300)}
