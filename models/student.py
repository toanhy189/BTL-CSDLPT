"""Mô hình dữ liệu/schema cho nghiệp vụ sinh viên."""

from dataclasses import dataclass


# Dataclass biểu diễn hồ sơ sinh viên và cơ sở quản lý sinh viên đó.
@dataclass
class Student:
    """Dataclass biểu diễn hồ sơ sinh viên và cơ sở quản lý sinh viên đó."""
    id: str
    name_student: str
    date_of_birth: str | None
    address_student: str | None
    formal_class: str | None
    year_of_admission: int | None
    phone_student: str | None
    id_department: str
    id_headquarter: str
