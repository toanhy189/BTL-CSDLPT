"""Các schema Pydantic mô tả dữ liệu request từ frontend gửi lên backend."""

from pydantic import BaseModel


# Schema dữ liệu đăng nhập gồm username và password.
class LoginRequest(BaseModel):
    username: str
    password: str


# Schema dữ liệu sinh viên gửi khi đăng ký một lớp học phần.
class RegisterRequest(BaseModel):
    student_id: str
    student_headquarter: str
    class_site_code: str
    class_id: str


# Schema dữ liệu sinh viên gửi khi hủy đăng ký học phần.
class CancelRequest(BaseModel):
    student_id: str
    class_site_code: str
    class_id: str


# Schema một sinh viên trong danh sách mô phỏng đăng ký đồng thời.
class StudentConcurrentItem(BaseModel):
    id_student: str
    id_student_headquarter: str


# Schema payload mô phỏng nhiều sinh viên cùng đăng ký một lớp.
class ConcurrentRegistrationRequest(BaseModel):
    class_site_code: str
    class_id: str
    students: list[StudentConcurrentItem]


# Schema chọn site/cơ sở để lọc hoặc ghi dữ liệu quản trị.
class SitePayload(BaseModel):
    site_code: str


class RegistrationStatusUpdate(BaseModel):
    registration_open: bool


class RegistrationPeriodStatusUpdate(BaseModel):
    is_open: bool

# Schema tạo mới cơ sở đào tạo.
class HeadquarterCreate(BaseModel):
    site_code: str
    id: str
    name_headquarter: str
    address: str | None = None


# Schema tạo mới sinh viên.
class StudentCreate(BaseModel):
    site_code: str
    id: str
    name_student: str
    date_of_birth: str | None = None
    address_student: str | None = None
    formal_class: str | None = None
    year_of_admission: int | None = None
    phone_student: str | None = None
    id_department: str
    id_headquarter: str


# Schema tạo mới giảng viên.
class TeacherCreate(BaseModel):
    site_code: str
    id: str
    name_teacher: str
    address_teacher: str | None = None
    degree: str | None = None
    phone_teacher: str | None = None
    id_department: str
    id_headquarter: str


# Schema tạo mới học phần.
class CourseCreate(BaseModel):
    id: str
    name_subject: str
    number_of_credit: int
    id_department: str


class TrainingProgramCreate(BaseModel):
    id_department: str
    id_subject: str
    suggested_semester: int | None = None
    is_required: bool = True


class RegistrationPeriodCreate(BaseModel):
    id: str
    semester: int
    school_year: int
    id_department: str
    admission_year: int | None = None
    start_time: str
    end_time: str
    is_open: bool = True
    description: str | None = None


# Schema tạo mới lớp học phần.
class ClassSectionCreate(BaseModel):
    site_code: str
    id: str
    semester: int | None = None
    school_year: int | None = None
    number_of_student: int = 0
    max_student: int
    id_subject: str
    id_teacher: str
    id_headquarter: str


# Schema tạo mới phòng học.
class RoomCreate(BaseModel):
    site_code: str
    id: str
    name_room: str
    capacity: int
    id_headquarter: str


# Schema tạo mới lịch học.
class ScheduleCreate(BaseModel):
    site_code: str
    id: str
    id_class: str
    study_date: str
    week_number: int | None = None
    day_of_week: int
    start_period: int
    end_period: int
    start_time: str
    end_time: str
    id_room: str
