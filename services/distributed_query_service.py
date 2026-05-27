"""Module phục vụ nghiệp vụ truy vấn phân tán service trong hệ thống đăng ký học phần phân tán."""

from db.distributed_queries import (
    danh_sach_lop_hoc_phan_toan_truong,
    hoc_phan_dang_ky_nhieu_nhat,
    sinh_vien_dang_ky_cheo_co_so,
    thong_ke_dang_ky_theo_co_so,
    thong_ke_sinh_vien_theo_co_so,
    thong_ke_so_lop_theo_co_so,
    ty_le_lap_day_lop_hoc_phan,
)


__all__ = [
    "thong_ke_dang_ky_theo_co_so",
    "hoc_phan_dang_ky_nhieu_nhat",
    "sinh_vien_dang_ky_cheo_co_so",
    "ty_le_lap_day_lop_hoc_phan",
    "thong_ke_so_lop_theo_co_so",
    "thong_ke_sinh_vien_theo_co_so",
    "danh_sach_lop_hoc_phan_toan_truong",
]
