"""Mô hình dữ liệu/schema cho nghiệp vụ học phần."""

from dataclasses import dataclass


# Dataclass biểu diễn học phần, gồm mã, tên, số tín chỉ và khoa phụ trách.
@dataclass
class Course:
    """Dataclass biểu diễn học phần, gồm mã, tên, số tín chỉ và khoa phụ trách."""
    id: str
    name_subject: str
    number_of_credit: int
    id_department: str
