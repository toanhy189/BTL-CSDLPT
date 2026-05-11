from dataclasses import dataclass


@dataclass
class ClassSection:
    id: str
    semester: int | None
    school_year: int | None
    number_of_student: int
    max_student: int
    shift: int | None
    id_subject: str
    id_teacher: str
    id_headquarter: str
