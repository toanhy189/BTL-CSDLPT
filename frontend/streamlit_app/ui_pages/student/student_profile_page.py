"""Trang Streamlit cho nghiệp vụ trang hồ sơ sinh viên, hiển thị dữ liệu và gửi thao tác của người dùng."""

from api_client import api_get
from styles import dataframe, metric_card, page_title


# Vẽ màn hình/khối giao diện sinh viên hồ sơ và gọi API hoặc service khi người dùng thao tác.
def render_student_profile(token):
    """Vẽ màn hình/khối giao diện sinh viên hồ sơ và gọi API hoặc service khi người dùng thao tác."""
    page_title("Hồ sơ cá nhân", "Thông tin sinh viên được đồng bộ từ cơ sở đào tạo.")
    data = api_get("/student-profile/me", token=token)
    if isinstance(data, dict) and data.get("_error"):
        metric_card("Không tải được hồ sơ", data.get("message"), icon="!", accent="red")
        return

    dataframe(
        [data] if data else [],
        height=220,
        rename={
            "id": "Mã sinh viên",
            "name_student": "Họ và tên",
            "date_of_birth": "Ngày sinh",
            "address_student": "Địa chỉ",
            "formal_class": "Lớp",
            "year_of_admission": "Năm nhập học",
            "phone_student": "Số điện thoại",
            "id_department": "Khoa",
            "id_headquarter": "Cơ sở",
        },
    )
