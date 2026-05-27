"""Module phục vụ nghiệp vụ test truy vấn trong hệ thống đăng ký học phần phân tán."""

import sys

from db.distributed_queries import (
    danh_sach_lop_hoc_phan_toan_truong,
    hoc_phan_dang_ky_nhieu_nhat,
    sinh_vien_dang_ky_cheo_co_so,
    thong_ke_dang_ky_theo_co_so,
    thong_ke_sinh_vien_theo_co_so,
    thong_ke_so_lop_theo_co_so,
    ty_le_lap_day_lop_hoc_phan,
)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


# In tiêu đề và DataFrame kết quả khi kiểm thử truy vấn từ terminal.
def print_result(title, df):
    """In tiêu đề và DataFrame kết quả khi kiểm thử truy vấn từ terminal."""
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)
    if df.empty:
        print("Khong co du lieu")
    else:
        print(df.to_string(index=False))


# Điểm vào của module, chuẩn bị dữ liệu/giao diện rồi điều phối sang luồng nghiệp vụ phù hợp.
def main():
    """Điểm vào của module, chuẩn bị dữ liệu/giao diện rồi điều phối sang luồng nghiệp vụ phù hợp."""
    queries = [
        ("1. Thong ke dang ky theo co so", thong_ke_dang_ky_theo_co_so),
        ("2. Hoc phan dang ky nhieu nhat", hoc_phan_dang_ky_nhieu_nhat),
        ("3. Sinh vien dang ky cheo co so", sinh_vien_dang_ky_cheo_co_so),
        ("4. Ty le lap day lop hoc phan", ty_le_lap_day_lop_hoc_phan),
        ("5. Thong ke so lop theo co so", thong_ke_so_lop_theo_co_so),
        ("6. Thong ke sinh vien theo co so", thong_ke_sinh_vien_theo_co_so),
        ("7. Danh sach lop hoc phan toan truong", danh_sach_lop_hoc_phan_toan_truong),
    ]

    for title, query_func in queries:
        print_result(title, query_func())


if __name__ == "__main__":
    main()
