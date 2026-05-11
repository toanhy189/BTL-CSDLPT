from dataclasses import dataclass


@dataclass
class Registration:
    id_student: str
    id_student_headquarter: str
    id_class: str
    registration_date: str | None
    status: str
