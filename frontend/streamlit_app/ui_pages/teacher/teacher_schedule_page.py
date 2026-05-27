"""Trang Streamlit cho nghiệp vụ trang lịch dạy giảng viên, hiển thị dữ liệu và gửi thao tác của người dùng."""

from api_client import api_get
from styles import dataframe, page_title, schedule_grid


# Vẽ màn hình/khối giao diện lịch dạy giảng viên và gọi API hoặc service khi người dùng thao tác.
def render_teacher_schedule(token):
    """Vẽ màn hình/khối giao diện lịch dạy giảng viên và gọi API hoặc service khi người dùng thao tác."""
    page_title("Lịch dạy", "Thời khóa biểu giảng dạy trong tuần.")
    data = api_get("/teacher/schedule", token=token)
    schedule_grid(data, "Thời khóa biểu giảng viên")
    dataframe(
        data,
        height=260,
        rename={
            "id_class": "Mã lớp",
            "name_subject": "Học phần",
            "day_of_week": "Thứ",
            "start_period": "Tiết bắt đầu",
            "end_period": "Tiết kết thúc",
            "id_room": "Phòng",
        },
        columns=["id_class", "name_subject", "day_of_week", "start_period", "end_period", "id_room"],
    )
