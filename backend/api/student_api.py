"""Router FastAPI cho nhóm nghiệp vụ sinh viên api, nhận request và chuyển xuống service phù hợp."""

from fastapi import APIRouter, Depends

from backend.core.security import require_role
from backend.db.queries import df_to_records, read_sql


router = APIRouter(prefix="/student-profile", tags=["student-profile"])


# Xử lý bước nghiệp vụ hồ sơ trong module này.
@router.get("/me")
def profile(current_user=Depends(require_role(["SINH_VIEN"]))):
    df = read_sql(current_user["id_headquarter"], "SELECT * FROM sinhvien WHERE id = %s;", (current_user["ref_id"],))
    records = df_to_records(df)
    return records[0] if records else {}
