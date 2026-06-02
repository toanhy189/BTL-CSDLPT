"""Tầng truy cập dữ liệu cho nghiệp vụ truy vấn, thực hiện đọc/ghi PostgreSQL theo site."""

import json
import warnings

import pandas as pd

from backend.core.config import SITE_CODES, SITE_NAMES
from backend.db.connections import get_connection


# Chuyển DataFrame sang list dict an toàn JSON trước khi trả qua API.
def df_to_records(df):
    if df is None or df.empty:
        return []
    safe_df = df.astype(object).where(pd.notnull(df), None)
    records = safe_df.to_dict(orient="records")
    return json.loads(json.dumps(records, default=str))


def _to_python_int(value):
    if pd.isna(value):
        return None
    return int(value)


# Đọc dữ liệu từ một site bằng pandas và trả DataFrame rỗng nếu truy vấn lỗi.
def read_sql(site_code, query, params=None):
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
    return read_sql(site_code, "SELECT * FROM khoa ORDER BY id;")


# Lấy dữ liệu cơ sở đào tạo từ nguồn phù hợp để trả về cho tầng gọi phía trên.
def get_headquarters(site_code):
    return read_sql(site_code, "SELECT * FROM coso ORDER BY id;")


# Lấy dữ liệu sinh viên từ nguồn phù hợp để trả về cho tầng gọi phía trên.
def get_students(site_code):
    return read_sql(site_code, "SELECT * FROM sinhvien ORDER BY id;")


# Thêm mới dữ liệu sinh viên sau khi nhận thông tin từ form hoặc API.
def add_student(site_code, data):
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


def update_student(site_code, student_id, data):
    return write_sql(
        site_code,
        """
        UPDATE sinhvien
        SET name_student = %s,
            date_of_birth = %s,
            address_student = %s,
            formal_class = %s,
            year_of_admission = %s,
            phone_student = %s,
            id_department = %s,
            id_headquarter = %s
        WHERE id = %s;
        """,
        (
            data["name_student"],
            data.get("date_of_birth"),
            data.get("address_student"),
            data.get("formal_class"),
            data.get("year_of_admission"),
            data.get("phone_student"),
            data["id_department"],
            data["id_headquarter"],
            student_id,
        ),
    )


def delete_student(site_code, student_id):
    return write_sql(site_code, "DELETE FROM sinhvien WHERE id = %s;", (student_id,))


# Lấy dữ liệu giảng viên từ nguồn phù hợp để trả về cho tầng gọi phía trên.
def get_teachers(site_code):
    return read_sql(site_code, "SELECT * FROM giangvien ORDER BY id;")


# Thêm mới dữ liệu giảng viên sau khi nhận thông tin từ form hoặc API.
def add_teacher(site_code, data):
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


def update_teacher(site_code, teacher_id, data):
    return write_sql(
        site_code,
        """
        UPDATE giangvien
        SET name_teacher = %s,
            address_teacher = %s,
            degree = %s,
            phone_teacher = %s,
            id_department = %s,
            id_headquarter = %s
        WHERE id = %s;
        """,
        (
            data["name_teacher"],
            data.get("address_teacher"),
            data.get("degree"),
            data.get("phone_teacher"),
            data["id_department"],
            data["id_headquarter"],
            teacher_id,
        ),
    )


def delete_teacher(site_code, teacher_id):
    return write_sql(site_code, "DELETE FROM giangvien WHERE id = %s;", (teacher_id,))


# Lấy dữ liệu học phần từ nguồn phù hợp để trả về cho tầng gọi phía trên.
def get_courses(site_code="HL"):
    return read_sql(site_code, "SELECT * FROM hocphan ORDER BY id;")


# Thêm mới dữ liệu học phần lên tất cả site sau khi nhận thông tin từ form hoặc API.
def add_course_to_all_sites(data):
    return write_all_sites(
        "INSERT INTO hocphan (id, name_subject, number_of_credit, id_department) VALUES (%s, %s, %s, %s);",
        (data["id"], data["name_subject"], data["number_of_credit"], data["id_department"]),
    )


def update_course_all_sites(course_id, data):
    return write_all_sites(
        """
        UPDATE hocphan
        SET name_subject = %s,
            number_of_credit = %s,
            id_department = %s
        WHERE id = %s;
        """,
        (data["name_subject"], data["number_of_credit"], data["id_department"], course_id),
    )


def delete_course_all_sites(course_id):
    return write_all_sites("DELETE FROM hocphan WHERE id = %s;", (course_id,))


def get_training_programs(site_code="HL"):
    return read_sql(
        site_code,
        """
        SELECT
            ctdt.id_department,
            k.name_department,
            ctdt.id_subject,
            hp.name_subject,
            ctdt.suggested_semester,
            ctdt.is_required
        FROM chuongtrinhdaotao ctdt
        JOIN khoa k ON k.id = ctdt.id_department
        JOIN hocphan hp ON hp.id = ctdt.id_subject
        ORDER BY ctdt.id_department, ctdt.suggested_semester NULLS LAST, ctdt.id_subject;
        """,
    )


def add_training_program_to_all_sites(data):
    return write_all_sites(
        """
        INSERT INTO chuongtrinhdaotao (id_department, id_subject, suggested_semester, is_required)
        VALUES (%s, %s, %s, %s);
        """,
        (data["id_department"], data["id_subject"], data.get("suggested_semester"), data.get("is_required", True)),
    )


def update_training_program_all_sites(department_id, subject_id, data):
    return write_all_sites(
        """
        UPDATE chuongtrinhdaotao
        SET suggested_semester = %s,
            is_required = %s
        WHERE id_department = %s AND id_subject = %s;
        """,
        (data.get("suggested_semester"), data.get("is_required", True), department_id, subject_id),
    )


def delete_training_program_all_sites(department_id, subject_id):
    return write_all_sites(
        "DELETE FROM chuongtrinhdaotao WHERE id_department = %s AND id_subject = %s;",
        (department_id, subject_id),
    )


def get_registration_periods(site_code="HL"):
    return read_sql(
        site_code,
        """
        SELECT
            ddk.id,
            ddk.semester,
            ddk.school_year,
            ddk.id_department,
            k.name_department,
            ddk.admission_year,
            ddk.start_time,
            ddk.end_time,
            ddk.is_open,
            ddk.description
        FROM dotdangky ddk
        JOIN khoa k ON k.id = ddk.id_department
        ORDER BY ddk.school_year DESC, ddk.semester DESC, ddk.id_department, ddk.admission_year;
        """,
    )


def add_registration_period_to_all_sites(data):
    return write_all_sites(
        """
        INSERT INTO dotdangky (
            id, semester, school_year, id_department, admission_year,
            start_time, end_time, is_open, description
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
        """,
        (
            data["id"],
            data["semester"],
            data["school_year"],
            data["id_department"],
            data.get("admission_year"),
            data["start_time"],
            data["end_time"],
            data.get("is_open", True),
            data.get("description"),
        ),
    )


def update_registration_period_all_sites(period_id, data):
    return write_all_sites(
        """
        UPDATE dotdangky
        SET semester = %s,
            school_year = %s,
            id_department = %s,
            admission_year = %s,
            start_time = %s,
            end_time = %s,
            is_open = %s,
            description = %s
        WHERE id = %s;
        """,
        (
            data["semester"],
            data["school_year"],
            data["id_department"],
            data.get("admission_year"),
            data["start_time"],
            data["end_time"],
            data.get("is_open", True),
            data.get("description"),
            period_id,
        ),
    )


def update_registration_period_status_all_sites(period_id, is_open):
    return write_all_sites(
        "UPDATE dotdangky SET is_open = %s WHERE id = %s;",
        (bool(is_open), period_id),
    )


def delete_registration_period_all_sites(period_id):
    return write_all_sites("DELETE FROM dotdangky WHERE id = %s;", (period_id,))


# Lấy dữ liệu phòng học từ nguồn phù hợp để trả về cho tầng gọi phía trên.
def get_rooms(site_code):
    return read_sql(site_code, "SELECT * FROM phonghoc ORDER BY id;")


# Thêm mới dữ liệu phòng học sau khi nhận thông tin từ form hoặc API.
def add_room(site_code, data):
    return write_sql(
        site_code,
        "INSERT INTO phonghoc (id, name_room, capacity, id_headquarter) VALUES (%s, %s, %s, %s);",
        (data["id"], data["name_room"], data["capacity"], data["id_headquarter"]),
    )


def update_room(site_code, room_id, data):
    return write_sql(
        site_code,
        """
        UPDATE phonghoc
        SET name_room = %s,
            capacity = %s,
            id_headquarter = %s
        WHERE id = %s;
        """,
        (data["name_room"], data["capacity"], data["id_headquarter"], room_id),
    )


def delete_room(site_code, room_id):
    return write_sql(site_code, "DELETE FROM phonghoc WHERE id = %s;", (room_id,))


# Lấy dữ liệu lớp học phần từ nguồn phù hợp để trả về cho tầng gọi phía trên.
def get_class_sections(site_code):
    return read_sql(
        site_code,
        """
        WITH schedule_sessions AS (
            SELECT
                id_class,
                day_of_week,
                start_period,
                end_period,
                start_time,
                end_time,
                id_room,
                MIN(study_date) AS first_study_date
            FROM lichhoc
            GROUP BY
                id_class, day_of_week, start_period, end_period,
                start_time, end_time, id_room
        )
        SELECT
            l.id,
            l.semester,
            l.school_year,
            l.number_of_student,
            l.max_student,
            l.id_subject,
            hp.name_subject,
            l.id_teacher,
            gv.name_teacher,
            l.id_headquarter,
            STRING_AGG(DISTINCT ss.id_room, ', ' ORDER BY ss.id_room) AS id_rooms,
            STRING_AGG(
                DISTINCT
                CASE ss.day_of_week
                    WHEN 2 THEN 'T2'
                    WHEN 3 THEN 'T3'
                    WHEN 4 THEN 'T4'
                    WHEN 5 THEN 'T5'
                    WHEN 6 THEN 'T6'
                    WHEN 7 THEN 'T7'
                    WHEN 8 THEN 'CN'
                END
                || ' ' || TO_CHAR(ss.first_study_date, 'DD/MM')
                || ', tiet ' || ss.start_period || '-' || ss.end_period
                || ', ' || TO_CHAR(ss.start_time, 'HH24:MI') || '-' || TO_CHAR(ss.end_time, 'HH24:MI')
                || ', ' || ss.id_room,
                E'\n'
            ) AS schedule_summary
        FROM lophocphan l
        JOIN hocphan hp ON hp.id = l.id_subject
        JOIN giangvien gv ON gv.id = l.id_teacher
        LEFT JOIN schedule_sessions ss ON ss.id_class = l.id
        GROUP BY
            l.id, l.semester, l.school_year, l.number_of_student, l.max_student,
            l.id_subject, hp.name_subject, l.id_teacher,
            gv.name_teacher, l.id_headquarter
        ORDER BY l.id;
        """,
    )


def get_open_class_sections_for_student(site_code, student_id, student_headquarter):
    """Lấy lớp học phần được phép đăng ký theo đợt đăng ký và CTĐT của sinh viên."""
    student_df = read_sql(
        student_headquarter,
        """
        SELECT id_department, year_of_admission
        FROM sinhvien
        WHERE id = %s;
        """,
        (student_id,),
    )
    if student_df.empty:
        return pd.DataFrame()
    student_department = student_df.iloc[0]["id_department"]
    admission_year = _to_python_int(student_df.iloc[0]["year_of_admission"])

    return read_sql(
        site_code,
        """
        WITH active_period AS (
            SELECT id, semester, school_year, id_department, admission_year, start_time, end_time, description
            FROM dotdangky
            WHERE id_department = %s
              AND (admission_year IS NULL OR admission_year = %s)
              AND is_open = true
              AND CURRENT_TIMESTAMP BETWEEN start_time AND end_time
            ORDER BY admission_year NULLS LAST, start_time DESC
            LIMIT 1
        ),
        schedule_sessions AS (
            SELECT
                id_class,
                day_of_week,
                start_period,
                end_period,
                start_time,
                end_time,
                id_room,
                MIN(study_date) AS first_study_date
            FROM lichhoc
            GROUP BY
                id_class, day_of_week, start_period, end_period,
                start_time, end_time, id_room
        )
        SELECT
            l.id,
            l.semester,
            l.school_year,
            l.number_of_student,
            l.max_student,
            l.id_subject,
            hp.name_subject,
            hp.id_department AS subject_department,
            l.id_teacher,
            gv.name_teacher,
            l.id_headquarter,
            ap.id AS registration_period_id,
            ap.description AS registration_period_description,
            ap.start_time AS registration_start_time,
            ap.end_time AS registration_end_time,
            ctdt.suggested_semester,
            ctdt.is_required,
            STRING_AGG(DISTINCT ss.id_room, ', ' ORDER BY ss.id_room) AS id_rooms,
            STRING_AGG(
                DISTINCT
                CASE ss.day_of_week
                    WHEN 2 THEN 'T2'
                    WHEN 3 THEN 'T3'
                    WHEN 4 THEN 'T4'
                    WHEN 5 THEN 'T5'
                    WHEN 6 THEN 'T6'
                    WHEN 7 THEN 'T7'
                    WHEN 8 THEN 'CN'
                END
                || ' ' || TO_CHAR(ss.first_study_date, 'DD/MM')
                || ', tiet ' || ss.start_period || '-' || ss.end_period
                || ', ' || TO_CHAR(ss.start_time, 'HH24:MI') || '-' || TO_CHAR(ss.end_time, 'HH24:MI')
                || ', ' || ss.id_room,
                E'\n'
            ) AS schedule_summary
        FROM active_period ap
        JOIN lophocphan l
          ON l.semester = ap.semester
         AND l.school_year = ap.school_year
        JOIN hocphan hp ON hp.id = l.id_subject
        JOIN chuongtrinhdaotao ctdt
          ON ctdt.id_department = ap.id_department
         AND ctdt.id_subject = hp.id
        JOIN giangvien gv ON gv.id = l.id_teacher
        LEFT JOIN schedule_sessions ss ON ss.id_class = l.id
        GROUP BY
            l.id, l.semester, l.school_year, l.number_of_student, l.max_student,
            l.id_subject, hp.name_subject, hp.id_department, l.id_teacher,
            gv.name_teacher, l.id_headquarter, ap.id, ap.description, ap.start_time,
            ap.end_time, ctdt.suggested_semester, ctdt.is_required
        ORDER BY ctdt.suggested_semester NULLS LAST, l.id;
        """,
        (student_department, admission_year),
    )


def get_active_registration_period_for_student(site_code, student_department, admission_year, semester, school_year):
    """Tìm đợt đăng ký hợp lệ trên site đang xử lý đăng ký."""
    admission_year = _to_python_int(admission_year)
    semester = _to_python_int(semester)
    school_year = _to_python_int(school_year)
    return read_sql(
        site_code,
        """
        SELECT id, semester, school_year, id_department, admission_year, start_time, end_time, description
        FROM dotdangky
        WHERE id_department = %s
          AND (admission_year IS NULL OR admission_year = %s)
          AND semester = %s
          AND school_year = %s
          AND is_open = true
          AND CURRENT_TIMESTAMP BETWEEN start_time AND end_time
        ORDER BY admission_year NULLS LAST, start_time DESC
        LIMIT 1;
        """,
        (student_department, admission_year, semester, school_year),
    )


# Thêm mới dữ liệu lớp học phần sau khi nhận thông tin từ form hoặc API.
def add_class_section(site_code, data):
    return write_sql(
        site_code,
        """
        INSERT INTO lophocphan (
            id, semester, school_year, number_of_student, max_student,
            id_subject, id_teacher, id_headquarter
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """,
        (
            data["id"],
            data.get("semester"),
            data.get("school_year"),
            data.get("number_of_student", 0),
            data["max_student"],
            data["id_subject"],
            data["id_teacher"],
            data["id_headquarter"],
        ),
    )


def update_class_section(site_code, class_id, data):
    return write_sql(
        site_code,
        """
        UPDATE lophocphan
        SET semester = %s,
            school_year = %s,
            max_student = %s,
            id_subject = %s,
            id_teacher = %s,
            id_headquarter = %s
        WHERE id = %s;
        """,
        (
            data.get("semester"),
            data.get("school_year"),
            data["max_student"],
            data["id_subject"],
            data["id_teacher"],
            data["id_headquarter"],
            class_id,
        ),
    )


def delete_class_section(site_code, class_id):
    return write_sql(site_code, "DELETE FROM lophocphan WHERE id = %s;", (class_id,))


# Lấy dữ liệu lịch học từ nguồn phù hợp để trả về cho tầng gọi phía trên.
def get_schedules(site_code):
    return read_sql(
        site_code,
        """
        SELECT
            lh.id,
            lh.id_class,
            hp.name_subject,
            lh.study_date,
            lh.week_number,
            lh.day_of_week,
            lh.start_period,
            lh.end_period,
            lh.start_time,
            lh.end_time,
            lh.id_room,
            ph.name_room
        FROM lichhoc lh
        JOIN lophocphan l ON l.id = lh.id_class
        JOIN hocphan hp ON hp.id = l.id_subject
        LEFT JOIN phonghoc ph ON ph.id = lh.id_room
        ORDER BY lh.study_date, lh.start_period, lh.id_class;
        """,
    )


# Thêm mới dữ liệu lịch học sau khi nhận thông tin từ form hoặc API.
def add_schedule(site_code, data):
    return write_sql(
        site_code,
        """
        INSERT INTO lichhoc (
            id, id_class, study_date, week_number, day_of_week,
            start_period, end_period, start_time, end_time, id_room
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """,
        (
            data["id"],
            data["id_class"],
            data["study_date"],
            data.get("week_number"),
            data["day_of_week"],
            data["start_period"],
            data["end_period"],
            data["start_time"],
            data["end_time"],
            data["id_room"],
        ),
    )


def update_schedule(site_code, schedule_id, data):
    return write_sql(
        site_code,
        """
        UPDATE lichhoc
        SET id_class = %s,
            study_date = %s,
            week_number = %s,
            day_of_week = %s,
            start_period = %s,
            end_period = %s,
            start_time = %s,
            end_time = %s,
            id_room = %s
        WHERE id = %s;
        """,
        (
            data["id_class"],
            data["study_date"],
            data.get("week_number"),
            data["day_of_week"],
            data["start_period"],
            data["end_period"],
            data["start_time"],
            data["end_time"],
            data["id_room"],
            schedule_id,
        ),
    )


def delete_schedule(site_code, schedule_id):
    return write_sql(site_code, "DELETE FROM lichhoc WHERE id = %s;", (schedule_id,))


# Lấy dữ liệu đăng ký theo sinh viên từ nguồn phù hợp để trả về cho tầng gọi phía trên.
def get_registration_by_student(student_id):
    frames = []
    query = """
        SELECT
            d.id_student,
            d.id_student_headquarter,
            d.id_class,
            hp.id AS id_subject,
            hp.name_subject,
            l.id_headquarter AS class_headquarter,
            d.id_registration_period,
            ddk.description AS registration_period_description,
            ddk.semester AS registration_semester,
            ddk.school_year AS registration_school_year,
            d.registration_date,
            d.status
        FROM dangky d
        JOIN lophocphan l ON l.id = d.id_class
        JOIN hocphan hp ON hp.id = l.id_subject
        JOIN dotdangky ddk ON ddk.id = d.id_registration_period
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


# Lấy dữ liệu đăng ký theo lớp từ nguồn phù hợp để trả về cho tầng gọi phía trên.
def get_registration_by_class(site_code, class_id):
    return read_sql(
        site_code,
        """
        SELECT
            d.id_student,
            d.id_student_headquarter,
            d.id_class,
            d.registration_date,
            d.status,
            d.id_registration_period,
            ddk.description AS registration_period_description,
            l.id_headquarter AS class_headquarter,
            hp.name_subject
        FROM dangky d
        JOIN lophocphan l ON l.id = d.id_class
        JOIN hocphan hp ON hp.id = l.id_subject
        JOIN dotdangky ddk ON ddk.id = d.id_registration_period
        WHERE d.id_class = %s
        ORDER BY d.registration_date DESC;
        """,
        (class_id,),
    )


# Lấy dữ liệu thời khóa biểu sinh viên từ nguồn phù hợp để trả về cho tầng gọi phía trên.
def get_student_schedule(student_id, semester=None, school_year=None, week_number=None):
    frames = []
    query = """
        SELECT
            d.id_student,
            d.id_class,
            hp.name_subject,
            lh.study_date,
            lh.week_number,
            lh.day_of_week,
            lh.start_period,
            lh.end_period,
            lh.start_time,
            lh.end_time,
            lh.id_room,
            l.id_headquarter AS class_headquarter
        FROM dangky d
        JOIN lophocphan l ON l.id = d.id_class
        JOIN hocphan hp ON hp.id = l.id_subject
        JOIN lichhoc lh ON lh.id_class = l.id
        WHERE d.id_student = %s
          AND d.status = 'DA_DANG_KY'
          AND (%s::int IS NULL OR l.semester = %s)
          AND (%s::int IS NULL OR l.school_year = %s)
          AND (%s::int IS NULL OR lh.week_number = %s)
        ORDER BY lh.study_date, lh.start_period;
    """
    for site_code in SITE_CODES:
        df = read_sql(site_code, query, (student_id, semester, semester, school_year, school_year, week_number, week_number))
        if not df.empty:
            df["site_code"] = site_code
            df["site_name"] = SITE_NAMES.get(site_code, site_code)
            frames.append(df)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


# Lấy dữ liệu lớp giảng viên phụ trách từ nguồn phù hợp để trả về cho tầng gọi phía trên.
def get_teacher_classes(teacher_id, site_code):
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
            l.id_headquarter
        FROM lophocphan l
        JOIN hocphan hp ON hp.id = l.id_subject
        WHERE l.id_teacher = %s
        ORDER BY l.id;
        """,
        (teacher_id,),
    )


# Lấy dữ liệu lịch dạy giảng viên từ nguồn phù hợp để trả về cho tầng gọi phía trên.
def get_teacher_schedule(teacher_id, site_code, semester=None, school_year=None, week_number=None):
    return read_sql(
        site_code,
        """
        SELECT
            l.id AS id_class,
            hp.name_subject,
            lh.study_date,
            lh.week_number,
            lh.day_of_week,
            lh.start_period,
            lh.end_period,
            lh.start_time,
            lh.end_time,
            lh.id_room
        FROM lophocphan l
        JOIN hocphan hp ON hp.id = l.id_subject
        JOIN lichhoc lh ON lh.id_class = l.id
        WHERE l.id_teacher = %s
          AND (%s::int IS NULL OR l.semester = %s)
          AND (%s::int IS NULL OR l.school_year = %s)
          AND (%s::int IS NULL OR lh.week_number = %s)
        ORDER BY lh.study_date, lh.start_period;
        """,
        (teacher_id, semester, semester, school_year, school_year, week_number, week_number),
    )
