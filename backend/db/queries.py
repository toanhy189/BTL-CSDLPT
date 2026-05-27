"""Tầng truy cập dữ liệu cho nghiệp vụ truy vấn, thực hiện đọc/ghi PostgreSQL theo site."""

import json
import warnings

import pandas as pd

from backend.core.config import SITE_CODES, SITE_NAMES
from backend.db.connections import get_connection


# Chuyển DataFrame sang list dict an toàn JSON trước khi trả qua API.
def df_to_records(df):
    """Chuyển DataFrame sang list dict an toàn JSON trước khi trả qua API."""
    if df is None or df.empty:
        return []
    safe_df = df.astype(object).where(pd.notnull(df), None)
    records = safe_df.to_dict(orient="records")
    return json.loads(json.dumps(records, default=str))


# Đọc dữ liệu từ một site bằng pandas và trả DataFrame rỗng nếu truy vấn lỗi.
def read_sql(site_code, query, params=None):
    """Đọc dữ liệu từ một site bằng pandas và trả DataFrame rỗng nếu truy vấn lỗi."""
    conn = None
    try:
        conn = get_connection(site_code)
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message="pandas only supports SQLAlchemy connectable.*",
                category=UserWarning,
            )
            return pd.read_sql(query, conn, params=params)
    except Exception as exc:
        print(f"[{site_code}] Lỗi đọc dữ liệu: {exc}")
        return pd.DataFrame()
    finally:
        if conn is not None:
            conn.close()


# Thực thi câu lệnh ghi dữ liệu trên một site với commit/rollback rõ ràng.
def write_sql(site_code, query, params=None):
    """Thực thi câu lệnh ghi dữ liệu trên một site với commit/rollback rõ ràng."""
    conn = None
    try:
        conn = get_connection(site_code)
        with conn.cursor() as cursor:
            cursor.execute(query, params)
        conn.commit()
        return True, "Thao tác thành công"
    except Exception as exc:
        if conn is not None:
            conn.rollback()
        return False, str(exc)
    finally:
        if conn is not None:
            conn.close()


# Các bảng danh mục dùng chung phải được ghi đồng bộ lên mọi site.
def write_all_sites(query, params=None):
    """Ghi cùng một thay đổi lên toàn bộ site, dùng cho dữ liệu cần nhân bản."""
    errors = []
    ok_count = 0
    for site_code in SITE_CODES:
        success, message = write_sql(site_code, query, params)
        if success:
            ok_count += 1
        else:
            errors.append(f"{site_code}: {message}")
    if errors:
        return False, f"Thành công {ok_count}/{len(SITE_CODES)} site. Lỗi: {'; '.join(errors)}"
    return True, "Thao tác thành công trên cả 5 site"


# Lấy dữ liệu khoa từ nguồn phù hợp để trả về cho tầng gọi phía trên.
def get_departments(site_code):
    """Lấy dữ liệu khoa từ nguồn phù hợp để trả về cho tầng gọi phía trên."""
    return read_sql(site_code, "SELECT * FROM khoa ORDER BY id;")


# Lấy dữ liệu cơ sở đào tạo từ nguồn phù hợp để trả về cho tầng gọi phía trên.
def get_headquarters(site_code):
    """Lấy dữ liệu cơ sở đào tạo từ nguồn phù hợp để trả về cho tầng gọi phía trên."""
    return read_sql(site_code, "SELECT * FROM coso ORDER BY id;")


# Lấy dữ liệu sinh viên từ nguồn phù hợp để trả về cho tầng gọi phía trên.
def get_students(site_code):
    """Lấy dữ liệu sinh viên từ nguồn phù hợp để trả về cho tầng gọi phía trên."""
    return read_sql(site_code, "SELECT * FROM sinhvien ORDER BY id;")


# Thêm mới dữ liệu sinh viên sau khi nhận thông tin từ form hoặc API.
def add_student(site_code, data):
    """Thêm mới dữ liệu sinh viên sau khi nhận thông tin từ form hoặc API."""
    return write_sql(
        site_code,
        """
        INSERT INTO sinhvien (
            id, name_student, date_of_birth, address_student, formal_class,
            year_of_admission, phone_student, id_department, id_headquarter
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
        """,
        (
            data["id"],
            data["name_student"],
            data.get("date_of_birth"),
            data.get("address_student"),
            data.get("formal_class"),
            data.get("year_of_admission"),
            data.get("phone_student"),
            data["id_department"],
            data["id_headquarter"],
        ),
    )


# Lấy dữ liệu giảng viên từ nguồn phù hợp để trả về cho tầng gọi phía trên.
def get_teachers(site_code):
    """Lấy dữ liệu giảng viên từ nguồn phù hợp để trả về cho tầng gọi phía trên."""
    return read_sql(site_code, "SELECT * FROM giangvien ORDER BY id;")


# Thêm mới dữ liệu giảng viên sau khi nhận thông tin từ form hoặc API.
def add_teacher(site_code, data):
    """Thêm mới dữ liệu giảng viên sau khi nhận thông tin từ form hoặc API."""
    return write_sql(
        site_code,
        """
        INSERT INTO giangvien (
            id, name_teacher, address_teacher, degree, phone_teacher,
            id_department, id_headquarter
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s);
        """,
        (
            data["id"],
            data["name_teacher"],
            data.get("address_teacher"),
            data.get("degree"),
            data.get("phone_teacher"),
            data["id_department"],
            data["id_headquarter"],
        ),
    )


# Lấy dữ liệu học phần từ nguồn phù hợp để trả về cho tầng gọi phía trên.
def get_courses(site_code="HL"):
    """Lấy dữ liệu học phần từ nguồn phù hợp để trả về cho tầng gọi phía trên."""
    return read_sql(site_code, "SELECT * FROM hocphan ORDER BY id;")


# Thêm mới dữ liệu học phần to all các site sau khi nhận thông tin từ form hoặc API.
def add_course_to_all_sites(data):
    """Thêm mới dữ liệu học phần to all các site sau khi nhận thông tin từ form hoặc API."""
    return write_all_sites(
        "INSERT INTO hocphan (id, name_subject, number_of_credit, id_department) VALUES (%s, %s, %s, %s);",
        (data["id"], data["name_subject"], data["number_of_credit"], data["id_department"]),
    )


# Lấy dữ liệu phòng học từ nguồn phù hợp để trả về cho tầng gọi phía trên.
def get_rooms(site_code):
    """Lấy dữ liệu phòng học từ nguồn phù hợp để trả về cho tầng gọi phía trên."""
    return read_sql(site_code, "SELECT * FROM phonghoc ORDER BY id;")


# Thêm mới dữ liệu phòng học sau khi nhận thông tin từ form hoặc API.
def add_room(site_code, data):
    """Thêm mới dữ liệu phòng học sau khi nhận thông tin từ form hoặc API."""
    return write_sql(
        site_code,
        "INSERT INTO phonghoc (id, name_room, capacity, id_headquarter) VALUES (%s, %s, %s, %s);",
        (data["id"], data["name_room"], data["capacity"], data["id_headquarter"]),
    )


# Lấy dữ liệu lớp học phần từ nguồn phù hợp để trả về cho tầng gọi phía trên.
def get_class_sections(site_code):
    """Lấy dữ liệu lớp học phần từ nguồn phù hợp để trả về cho tầng gọi phía trên."""
    return read_sql(
        site_code,
        """
        SELECT
            l.id,
            l.semester,
            l.school_year,
            l.number_of_student,
            l.max_student,
            l.shift,
            l.id_subject,
            hp.name_subject,
            l.id_teacher,
            gv.name_teacher,
            l.id_headquarter,
            STRING_AGG(DISTINCT lh.id_room, ', ' ORDER BY lh.id_room) AS id_rooms
        FROM lophocphan l
        JOIN hocphan hp ON hp.id = l.id_subject
        JOIN giangvien gv ON gv.id = l.id_teacher
        LEFT JOIN lichhoc lh ON lh.id_class = l.id
        GROUP BY
            l.id, l.semester, l.school_year, l.number_of_student, l.max_student,
            l.shift, l.id_subject, hp.name_subject, l.id_teacher,
            gv.name_teacher, l.id_headquarter
        ORDER BY l.id;
        """,
    )


# Thêm mới dữ liệu lớp học phần sau khi nhận thông tin từ form hoặc API.
def add_class_section(site_code, data):
    """Thêm mới dữ liệu lớp học phần sau khi nhận thông tin từ form hoặc API."""
    return write_sql(
        site_code,
        """
        INSERT INTO lophocphan (
            id, semester, school_year, number_of_student, max_student,
            shift, id_subject, id_teacher, id_headquarter
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
        """,
        (
            data["id"],
            data.get("semester"),
            data.get("school_year"),
            data.get("number_of_student", 0),
            data["max_student"],
            data.get("shift"),
            data["id_subject"],
            data["id_teacher"],
            data["id_headquarter"],
        ),
    )


# Lấy dữ liệu lịch học từ nguồn phù hợp để trả về cho tầng gọi phía trên.
def get_schedules(site_code):
    """Lấy dữ liệu lịch học từ nguồn phù hợp để trả về cho tầng gọi phía trên."""
    return read_sql(
        site_code,
        """
        SELECT
            lh.id,
            lh.id_class,
            hp.name_subject,
            lh.day_of_week,
            lh.start_period,
            lh.end_period,
            lh.id_room,
            ph.name_room
        FROM lichhoc lh
        JOIN lophocphan l ON l.id = lh.id_class
        JOIN hocphan hp ON hp.id = l.id_subject
        LEFT JOIN phonghoc ph ON ph.id = lh.id_room
        ORDER BY lh.day_of_week, lh.start_period, lh.id_class;
        """,
    )


# Thêm mới dữ liệu lịch học sau khi nhận thông tin từ form hoặc API.
def add_schedule(site_code, data):
    """Thêm mới dữ liệu lịch học sau khi nhận thông tin từ form hoặc API."""
    return write_sql(
        site_code,
        """
        INSERT INTO lichhoc (id, id_class, day_of_week, start_period, end_period, id_room)
        VALUES (%s, %s, %s, %s, %s, %s);
        """,
        (
            data["id"],
            data["id_class"],
            data["day_of_week"],
            data["start_period"],
            data["end_period"],
            data["id_room"],
        ),
    )


# Lấy dữ liệu registration by sinh viên từ nguồn phù hợp để trả về cho tầng gọi phía trên.
def get_registration_by_student(student_id):
    """Lấy dữ liệu registration by sinh viên từ nguồn phù hợp để trả về cho tầng gọi phía trên."""
    frames = []
    query = """
        SELECT
            d.id_student,
            d.id_student_headquarter,
            d.id_class,
            hp.name_subject,
            l.id_headquarter AS class_headquarter,
            d.registration_date,
            d.status
        FROM dangky d
        JOIN lophocphan l ON l.id = d.id_class
        JOIN hocphan hp ON hp.id = l.id_subject
        WHERE d.id_student = %s
        ORDER BY d.registration_date DESC;
    """
    for site_code in SITE_CODES:
        df = read_sql(site_code, query, (student_id,))
        if not df.empty:
            df["site_code"] = site_code
            df["site_name"] = SITE_NAMES.get(site_code, site_code)
            frames.append(df)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


# Lấy dữ liệu registration by class từ nguồn phù hợp để trả về cho tầng gọi phía trên.
def get_registration_by_class(site_code, class_id):
    """Lấy dữ liệu registration by class từ nguồn phù hợp để trả về cho tầng gọi phía trên."""
    return read_sql(
        site_code,
        """
        SELECT
            d.id_student,
            d.id_student_headquarter,
            d.id_class,
            d.registration_date,
            d.status,
            l.id_headquarter AS class_headquarter,
            hp.name_subject
        FROM dangky d
        JOIN lophocphan l ON l.id = d.id_class
        JOIN hocphan hp ON hp.id = l.id_subject
        WHERE d.id_class = %s
        ORDER BY d.registration_date DESC;
        """,
        (class_id,),
    )


# Lấy dữ liệu thời khóa biểu sinh viên từ nguồn phù hợp để trả về cho tầng gọi phía trên.
def get_student_schedule(student_id):
    """Lấy dữ liệu thời khóa biểu sinh viên từ nguồn phù hợp để trả về cho tầng gọi phía trên."""
    frames = []
    query = """
        SELECT
            d.id_student,
            d.id_class,
            hp.name_subject,
            lh.day_of_week,
            lh.start_period,
            lh.end_period,
            lh.id_room,
            l.id_headquarter AS class_headquarter
        FROM dangky d
        JOIN lophocphan l ON l.id = d.id_class
        JOIN hocphan hp ON hp.id = l.id_subject
        JOIN lichhoc lh ON lh.id_class = l.id
        WHERE d.id_student = %s AND d.status = 'DA_DANG_KY'
        ORDER BY lh.day_of_week, lh.start_period;
    """
    for site_code in SITE_CODES:
        df = read_sql(site_code, query, (student_id,))
        if not df.empty:
            df["site_code"] = site_code
            df["site_name"] = SITE_NAMES.get(site_code, site_code)
            frames.append(df)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


# Lấy dữ liệu lớp giảng viên phụ trách từ nguồn phù hợp để trả về cho tầng gọi phía trên.
def get_teacher_classes(teacher_id, site_code):
    """Lấy dữ liệu lớp giảng viên phụ trách từ nguồn phù hợp để trả về cho tầng gọi phía trên."""
    return read_sql(
        site_code,
        """
        SELECT
            l.id,
            hp.name_subject,
            l.semester,
            l.school_year,
            l.number_of_student,
            l.max_student,
            l.shift,
            l.id_headquarter
        FROM lophocphan l
        JOIN hocphan hp ON hp.id = l.id_subject
        WHERE l.id_teacher = %s
        ORDER BY l.id;
        """,
        (teacher_id,),
    )


# Lấy dữ liệu lịch dạy giảng viên từ nguồn phù hợp để trả về cho tầng gọi phía trên.
def get_teacher_schedule(teacher_id, site_code):
    """Lấy dữ liệu lịch dạy giảng viên từ nguồn phù hợp để trả về cho tầng gọi phía trên."""
    return read_sql(
        site_code,
        """
        SELECT
            l.id AS id_class,
            hp.name_subject,
            lh.day_of_week,
            lh.start_period,
            lh.end_period,
            lh.id_room
        FROM lophocphan l
        JOIN hocphan hp ON hp.id = l.id_subject
        JOIN lichhoc lh ON lh.id_class = l.id
        WHERE l.id_teacher = %s
        ORDER BY lh.day_of_week, lh.start_period;
        """,
        (teacher_id,),
    )
