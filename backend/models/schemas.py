"""Các schema Pydantic mô tả dữ liệu request từ frontend gửi lên backend."""

from pydantic import BaseModel


# Schema dữ liệu đăng nhập gồm username và password.
class LoginRequest(BaseModel):
    """Schema dữ liệu đăng nhập gồm username và password."""
    username: str
    password: str


# Schema dữ liệu sinh viên gửi khi đăng ký một lớp học phần.
class RegisterRequest(BaseModel):
    """Schema dữ liệu sinh viên gửi khi đăng ký một lớp học phần."""
    student_id: str
    student_headquarter: str
    class_site_code: str
    class_id: str


# Schema dữ liệu sinh viên gửi khi hủy đăng ký học phần.
class CancelRequest(BaseModel):
    """Schema dữ liệu sinh viên gửi khi hủy đăng ký học phần."""
    student_id: str
    class_site_code: str
    class_id: str


# Schema một sinh viên trong danh sách mô phỏng đăng ký đồng thời.
class StudentConcurrentItem(BaseModel):
    """Schema một sinh viên trong danh sách mô phỏng đăng ký đồng thời."""
    id_student: str
    id_student_headquarter: str


# Schema payload mô phỏng nhiều sinh viên cùng đăng ký một lớp.
class ConcurrentRegistrationRequest(BaseModel):
    """Schema payload mô phỏng nhiều sinh viên cùng đăng ký một lớp."""
    class_site_code: str
    class_id: str
    students: list[StudentConcurrentItem]


# Schema chọn site/cơ sở để lọc hoặc ghi dữ liệu quản trị.
class SitePayload(BaseModel):
    """Schema chọn site/cơ sở để lọc hoặc ghi dữ liệu quản trị."""
    site_code: str


# Schema tạo mới cơ sở đào tạo.
class HeadquarterCreate(BaseModel):
    """Schema tạo mới cơ sở đào tạo."""
    site_code: str
    id: str
    name_headquarter: str
    address: str | None = None


# Schema tạo mới sinh viên.
class StudentCreate(BaseModel):
    """Schema tạo mới sinh viên."""
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
    """Schema tạo mới giảng viên."""
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
    """Schema tạo mới học phần."""
    id: str
    name_subject: str
    number_of_credit: int
    id_department: str


# Schema tạo mới lớp học phần.
class ClassSectionCreate(BaseModel):
    """Schema tạo mới lớp học phần."""
    site_code: str
    id: str
    semester: int | None = None
    school_year: int | None = None
    number_of_student: int = 0
    max_student: int
    shift: int | None = None
    id_subject: str
    id_teacher: str
    id_headquarter: str


# Schema tạo mới phòng học.
class RoomCreate(BaseModel):
    """Schema tạo mới phòng học."""
    site_code: str
    id: str
    name_room: str
    capacity: int
    id_headquarter: str


# Schema tạo mới lịch học.
class ScheduleCreate(BaseModel):
    """Schema tạo mới lịch học."""
    site_code: str
    id: str
    id_class: str
    day_of_week: int
    start_period: int
    end_period: int
    id_room: str
