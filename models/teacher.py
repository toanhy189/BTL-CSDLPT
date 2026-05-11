from dataclasses import dataclass


@dataclass
class Teacher:
    id: str
    name_teacher: str
    address_teacher: str | None
    degree: str | None
    phone_teacher: str | None
    id_department: str
    id_headquarter: str
