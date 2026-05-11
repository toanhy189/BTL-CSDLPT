from dataclasses import dataclass


@dataclass
class Student:
    id: str
    name_student: str
    date_of_birth: str | None
    address_student: str | None
    formal_class: str | None
    year_of_admission: int | None
    phone_student: str | None
    id_department: str
    id_headquarter: str
