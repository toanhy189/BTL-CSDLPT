"""CRUD queries cho tung site PostgreSQL."""

import warnings

import pandas as pd

from db.connections import SITE_CODES, SITE_NAMES, get_connection


def _read_sql(site_code, query, params=None):
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
        print(f"[{site_code}] Loi doc du lieu: {exc}")
        return pd.DataFrame()
    finally:
        if conn is not None:
            conn.close()


def _write_sql(site_code, query, params=None):
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


def _write_all_sites(query, params=None):
    messages = []
    ok_count = 0
    for site_code in SITE_CODES:
        success, message = _write_sql(site_code, query, params)
        if success:
            ok_count += 1
        else:
            messages.append(f"{site_code}: {message}")

    if messages:
        return False, f"Thành công {ok_count}/{len(SITE_CODES)} site. Lỗi: " + "; ".join(messages)
    return True, "Thao tác thành công trên cả 5 site"


def _empty_to_none(value):
    return None if value == "" else value


def get_all_sites_table(site_code):
    return get_headquarters(site_code)


def get_departments(site_code):
    return _read_sql(site_code, "SELECT * FROM khoa ORDER BY id;")


def get_subjects(site_code):
    return _read_sql(site_code, "SELECT * FROM hocphan ORDER BY id;")


def get_headquarters(site_code):
    return _read_sql(site_code, "SELECT * FROM coso ORDER BY id;")


def add_headquarter(site_code, id, name_headquarter, address):
    return _write_sql(
        site_code,
        "INSERT INTO coso (id, name_headquarter, address) VALUES (%s, %s, %s);",
        (id, name_headquarter, _empty_to_none(address)),
    )


def update_headquarter(site_code, id, name_headquarter, address):
    return _write_sql(
        site_code,
        "UPDATE coso SET name_headquarter = %s, address = %s WHERE id = %s;",
        (name_headquarter, _empty_to_none(address), id),
    )


def delete_headquarter(site_code, id):
    return _write_sql(site_code, "DELETE FROM coso WHERE id = %s;", (id,))


def get_students(site_code):
    return _read_sql(site_code, "SELECT * FROM sinhvien ORDER BY id;")


def add_student(site_code, data):
    return _write_sql(
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
            _empty_to_none(data.get("date_of_birth")),
            _empty_to_none(data.get("address_student")),
            _empty_to_none(data.get("formal_class")),
            data.get("year_of_admission"),
            _empty_to_none(data.get("phone_student")),
            data["id_department"],
            data["id_headquarter"],
        ),
    )


def update_student(site_code, student_id, data):
    return _write_sql(
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
            _empty_to_none(data.get("date_of_birth")),
            _empty_to_none(data.get("address_student")),
            _empty_to_none(data.get("formal_class")),
            data.get("year_of_admission"),
            _empty_to_none(data.get("phone_student")),
            data["id_department"],
            data["id_headquarter"],
            student_id,
        ),
    )


def delete_student(site_code, student_id):
    return _write_sql(site_code, "DELETE FROM sinhvien WHERE id = %s;", (student_id,))


def get_teachers(site_code):
    return _read_sql(site_code, "SELECT * FROM giangvien ORDER BY id;")


def add_teacher(site_code, data):
    return _write_sql(
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
            _empty_to_none(data.get("address_teacher")),
            _empty_to_none(data.get("degree")),
            _empty_to_none(data.get("phone_teacher")),
            data["id_department"],
            data["id_headquarter"],
        ),
    )


def update_teacher(site_code, teacher_id, data):
    return _write_sql(
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
            _empty_to_none(data.get("address_teacher")),
            _empty_to_none(data.get("degree")),
            _empty_to_none(data.get("phone_teacher")),
            data["id_department"],
            data["id_headquarter"],
            teacher_id,
        ),
    )


def delete_teacher(site_code, teacher_id):
    return _write_sql(site_code, "DELETE FROM giangvien WHERE id = %s;", (teacher_id,))


def get_courses(site_code):
    return _read_sql(site_code, "SELECT * FROM hocphan ORDER BY id;")


def add_course_to_all_sites(data):
    return _write_all_sites(
        "INSERT INTO hocphan (id, name_subject, number_of_credit, id_department) VALUES (%s, %s, %s, %s);",
        (data["id"], data["name_subject"], data["number_of_credit"], data["id_department"]),
    )


def update_course_all_sites(course_id, data):
    return _write_all_sites(
        """
        UPDATE hocphan
        SET name_subject = %s, number_of_credit = %s, id_department = %s
        WHERE id = %s;
        """,
        (data["name_subject"], data["number_of_credit"], data["id_department"], course_id),
    )


def delete_course_all_sites(course_id):
    return _write_all_sites("DELETE FROM hocphan WHERE id = %s;", (course_id,))


def get_rooms(site_code):
    return _read_sql(site_code, "SELECT * FROM phonghoc ORDER BY id;")


def add_room(site_code, data):
    return _write_sql(
        site_code,
        "INSERT INTO phonghoc (id, name_room, capacity, id_headquarter) VALUES (%s, %s, %s, %s);",
        (data["id"], data["name_room"], data["capacity"], data["id_headquarter"]),
    )


def update_room(site_code, room_id, data):
    return _write_sql(
        site_code,
        "UPDATE phonghoc SET name_room = %s, capacity = %s, id_headquarter = %s WHERE id = %s;",
        (data["name_room"], data["capacity"], data["id_headquarter"], room_id),
    )


def delete_room(site_code, room_id):
    return _write_sql(site_code, "DELETE FROM phonghoc WHERE id = %s;", (room_id,))


def get_class_sections(site_code):
    return _read_sql(
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


def add_class_section(site_code, data):
    return _write_sql(
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


def update_class_section(site_code, class_id, data):
    return _write_sql(
        site_code,
        """
        UPDATE lophocphan
        SET semester = %s,
            school_year = %s,
            number_of_student = %s,
            max_student = %s,
            shift = %s,
            id_subject = %s,
            id_teacher = %s,
            id_headquarter = %s
        WHERE id = %s;
        """,
        (
            data.get("semester"),
            data.get("school_year"),
            data.get("number_of_student", 0),
            data["max_student"],
            data.get("shift"),
            data["id_subject"],
            data["id_teacher"],
            data["id_headquarter"],
            class_id,
        ),
    )


def delete_class_section(site_code, class_id):
    return _write_sql(site_code, "DELETE FROM lophocphan WHERE id = %s;", (class_id,))


def get_schedules(site_code):
    return _read_sql(
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
        ORDER BY lh.id_class, lh.day_of_week, lh.start_period;
        """,
    )


def add_schedule(site_code, data):
    return _write_sql(
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
            _empty_to_none(data.get("id_room")),
        ),
    )


def update_schedule(site_code, schedule_id, data):
    return _write_sql(
        site_code,
        """
        UPDATE lichhoc
        SET id_class = %s, day_of_week = %s, start_period = %s, end_period = %s, id_room = %s
        WHERE id = %s;
        """,
        (
            data["id_class"],
            data["day_of_week"],
            data["start_period"],
            data["end_period"],
            _empty_to_none(data.get("id_room")),
            schedule_id,
        ),
    )


def delete_schedule(site_code, schedule_id):
    return _write_sql(site_code, "DELETE FROM lichhoc WHERE id = %s;", (schedule_id,))


def get_registration_by_student(student_id):
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
        df = _read_sql(site_code, query, (student_id,))
        if not df.empty:
            df["site_code"] = site_code
            df["site_name"] = SITE_NAMES.get(site_code, site_code)
            frames.append(df)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def get_registration_by_class(site_code, class_id):
    return _read_sql(
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
