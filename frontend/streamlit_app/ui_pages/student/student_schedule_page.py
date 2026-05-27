"""Trang Streamlit cho nghiệp vụ trang thời khóa biểu sinh viên, hiển thị dữ liệu và gửi thao tác của người dùng."""

from api_client import api_get
from styles import dataframe, page_title, schedule_grid


# Vẽ màn hình/khối giao diện thời khóa biểu sinh viên và gọi API hoặc service khi người dùng thao tác.
def render_student_schedule(token):
    """Vẽ màn hình/khối giao diện thời khóa biểu sinh viên và gọi API hoặc service khi người dùng thao tác."""
    page_title("Thời khóa biểu", "Lịch học theo các học phần đã đăng ký.")
    data = api_get("/student/schedule", token=token)
    schedule_grid(data, "Lịch học trong tuần")
    dataframe(
        data,
        height=260,
        rename={
            "id_class": "Mã lớp",
            "name_subject": "Tên học phần",
            "day_of_week": "Thứ",
            "start_period": "Tiết bắt đầu",
            "end_period": "Tiết kết thúc",
            "id_room": "Phòng",
            "class_headquarter": "Cơ sở",
        },
        columns=["id_class", "name_subject", "day_of_week", "start_period", "end_period", "id_room", "class_headquarter"],
    )
