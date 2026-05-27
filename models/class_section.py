"""Mô hình dữ liệu/schema cho nghiệp vụ lớp học phần."""

from dataclasses import dataclass


# Dataclass biểu diễn lớp học phần, gồm học kỳ, sĩ số, học phần, giảng viên và cơ sở mở lớp.
@dataclass
class ClassSection:
    """Dataclass biểu diễn lớp học phần, gồm học kỳ, sĩ số, học phần, giảng viên và cơ sở mở lớp."""
    id: str
    semester: int | None
    school_year: int | None
    number_of_student: int
    max_student: int
    shift: int | None
    id_subject: str
    id_teacher: str
    id_headquarter: str
