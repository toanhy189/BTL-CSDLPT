"""Mô hình dữ liệu/schema cho nghiệp vụ registration."""

from dataclasses import dataclass


# Dataclass biểu diễn một lượt sinh viên đăng ký vào lớp học phần.
@dataclass
class Registration:
    """Dataclass biểu diễn một lượt sinh viên đăng ký vào lớp học phần."""
    id_student: str
    id_student_headquarter: str
    id_class: str
    registration_date: str | None
    status: str
