"""Router FastAPI cho nhóm nghiệp vụ truy vấn phân tán api, nhận request và chuyển xuống service phù hợp."""

from fastapi import APIRouter, Depends

from backend.core.security import require_role
from backend.db.queries import df_to_records
from backend.services import distributed_query_service as service


router = APIRouter(
    prefix="/distributed",
    tags=["distributed"],
    dependencies=[Depends(require_role(["ADMIN"]))],
)


# Xử lý bước nghiệp vụ thống kê đăng ký theo cơ sở trong module này.
@router.get("/registration-by-site")
def registration_by_site():
    """Xử lý bước nghiệp vụ thống kê đăng ký theo cơ sở trong module này."""
    return df_to_records(service.thong_ke_dang_ky_theo_co_so())


# Xử lý bước nghiệp vụ học phần đăng ký nhiều nhất trong module này.
@router.get("/top-courses")
def top_courses():
    """Xử lý bước nghiệp vụ học phần đăng ký nhiều nhất trong module này."""
    return df_to_records(service.hoc_phan_dang_ky_nhieu_nhat())


# Xử lý bước nghiệp vụ sinh viên đăng ký chéo cơ sở trong module này.
@router.get("/cross-site-students")
def cross_site_students():
    """Xử lý bước nghiệp vụ sinh viên đăng ký chéo cơ sở trong module này."""
    return df_to_records(service.sinh_vien_dang_ky_cheo_co_so())


# Xử lý bước nghiệp vụ tỷ lệ lấp đầy lớp học phần trong module này.
@router.get("/fill-rate")
def fill_rate():
    """Xử lý bước nghiệp vụ tỷ lệ lấp đầy lớp học phần trong module này."""
    return df_to_records(service.ty_le_lap_day_lop_hoc_phan())


# Xử lý bước nghiệp vụ số lớp học phần theo cơ sở trong module này.
@router.get("/classes-by-site")
def classes_by_site():
    """Xử lý bước nghiệp vụ số lớp học phần theo cơ sở trong module này."""
    return df_to_records(service.thong_ke_so_lop_theo_co_so())


# Xử lý bước nghiệp vụ số sinh viên theo cơ sở trong module này.
@router.get("/students-by-site")
def students_by_site():
    """Xử lý bước nghiệp vụ số sinh viên theo cơ sở trong module này."""
    return df_to_records(service.thong_ke_sinh_vien_theo_co_so())
