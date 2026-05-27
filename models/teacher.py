"""Mô hình dữ liệu/schema cho nghiệp vụ giảng viên."""

from dataclasses import dataclass


# Dataclass biểu diễn hồ sơ giảng viên, học vị, khoa và cơ sở công tác.
@dataclass
class Teacher:
    """Dataclass biểu diễn hồ sơ giảng viên, học vị, khoa và cơ sở công tác."""
    id: str
    name_teacher: str
    address_teacher: str | None
    degree: str | None
    phone_teacher: str | None
    id_department: str
    id_headquarter: str
