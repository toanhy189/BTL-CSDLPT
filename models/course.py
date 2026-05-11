from dataclasses import dataclass


@dataclass
class Course:
    id: str
    name_subject: str
    number_of_credit: int
    id_department: str
