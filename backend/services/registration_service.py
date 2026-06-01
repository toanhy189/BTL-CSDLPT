"""Course registration service with row locks and concurrent registration demo."""

from datetime import datetime
import threading

import pandas as pd

from backend.db.connections import get_connection
from backend.core.registration_config import is_registration_open
from backend.core.config import SITE_CODES
from backend.services.log_service import write_log


def _subject_key(class_row):
    """Return the logical subject offering key: subject + semester + school year."""
    return f"{class_row[3]}:{class_row[1]}:{class_row[2]}"


def _get_class_metadata(cursor, class_id):
    cursor.execute(
        """
        SELECT id, semester, school_year, id_subject, number_of_student, max_student
        FROM lophocphan
        WHERE id = %s;
        """,
        (class_id,),
    )
    return cursor.fetchone()


def _get_student_info(student_id, student_headquarter):
    conn = None
    try:
        conn = get_connection(student_headquarter)
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id_department, year_of_admission
                FROM sinhvien
                WHERE id = %s;
                """,
                (student_id,),
            )
            return cursor.fetchone()
    finally:
        if conn:
            conn.close()


def _get_active_registration_period(cursor, student_department, admission_year, semester, school_year):
    cursor.execute(
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
    return cursor.fetchone()


def _subject_in_training_program(cursor, student_department, subject_id):
    cursor.execute(
        """
        SELECT 1
        FROM chuongtrinhdaotao
        WHERE id_department = %s AND id_subject = %s;
        """,
        (student_department, subject_id),
    )
    return cursor.fetchone() is not None


def _find_active_classes_for_same_subject(cursor, student_id, target_class):
    cursor.execute(
        """
        SELECT d.id_class
        FROM dangky d
        JOIN lophocphan old_lhp ON old_lhp.id = d.id_class
        WHERE d.id_student = %s
          AND d.status = 'DA_DANG_KY'
          AND old_lhp.id_subject = %s
          AND old_lhp.semester IS NOT DISTINCT FROM %s
          AND old_lhp.school_year IS NOT DISTINCT FROM %s
        ORDER BY d.id_class;
        """,
        (student_id, target_class[3], target_class[1], target_class[2]),
    )
    return [row[0] for row in cursor.fetchall()]


def _lock_classes_in_fixed_order(cursor, class_ids):
    ordered_ids = sorted(set(class_ids))
    cursor.execute(
        """
        SELECT id, semester, school_year, id_subject, number_of_student, max_student
        FROM lophocphan
        WHERE id = ANY(%s)
        ORDER BY id
        FOR UPDATE;
        """,
        (ordered_ids,),
    )
    rows = cursor.fetchall()
    if len(rows) != len(ordered_ids):
        return None
    return {row[0]: row for row in rows}


def _lock_student_active_registrations(cursor, student_id):
    cursor.execute(
        """
        SELECT id_class
        FROM dangky
        WHERE id_student = %s AND status = 'DA_DANG_KY'
        ORDER BY id_class
        FOR UPDATE;
        """,
        (student_id,),
    )
    cursor.fetchall()


def _get_class_schedule(cursor, class_id):
    cursor.execute(
        """
        SELECT study_date, start_period, end_period
        FROM lichhoc
        WHERE id_class = %s
        ORDER BY study_date, start_period;
        """,
        (class_id,),
    )
    return cursor.fetchall()


def _find_schedule_conflict_at_site(cursor, student_id, target_schedules, ignored_class_id):
    for study_date, start_period, end_period in target_schedules:
        cursor.execute(
            """
            SELECT
                d.id_class,
                hp.name_subject,
                lh.study_date,
                lh.start_period,
                lh.end_period
            FROM dangky d
            JOIN lophocphan l ON l.id = d.id_class
            JOIN hocphan hp ON hp.id = l.id_subject
            JOIN lichhoc lh ON lh.id_class = l.id
            WHERE d.id_student = %s
              AND d.status = 'DA_DANG_KY'
              AND d.id_class <> %s
              AND lh.study_date = %s
              AND lh.start_period <= %s
              AND %s <= lh.end_period
            ORDER BY lh.study_date, lh.start_period, d.id_class
            LIMIT 1;
            """,
            (student_id, ignored_class_id, study_date, end_period, start_period),
        )
        conflict = cursor.fetchone()
        if conflict:
            return conflict
    return None


def _find_schedule_conflict(student_id, class_site_code, current_cursor, class_id, ignored_class_id):
    target_schedules = _get_class_schedule(current_cursor, class_id)
    if not target_schedules:
        return None

    conflict = _find_schedule_conflict_at_site(
        current_cursor,
        student_id,
        target_schedules,
        ignored_class_id,
    )
    if conflict:
        return {"conflict": conflict, "site_code": class_site_code}

    for site_code in SITE_CODES:
        if site_code == class_site_code:
            continue
        conn = None
        try:
            conn = get_connection(site_code)
            with conn.cursor() as cursor:
                cursor.execute("SET LOCAL statement_timeout = '10s';")
                conflict = _find_schedule_conflict_at_site(
                    cursor,
                    student_id,
                    target_schedules,
                    ignored_class_id,
                )
                if conflict:
                    return {"conflict": conflict, "site_code": site_code}
        except Exception as exc:
            write_log(f"SITE_DOWN site={site_code} action=KIEM_TRA_TRUNG_LICH student={student_id} class={class_id} error={exc}")
            return {"error": f"Khong kiem tra duoc lich hoc tai site {site_code}: {exc}"}
        finally:
            if conn:
                conn.close()
    return None


def _activate_registration(cursor, student_id, student_headquarter, class_id, registration_period_id):
    cursor.execute(
        """
        SELECT status
        FROM dangky
        WHERE id_student = %s AND id_class = %s
        FOR UPDATE;
        """,
        (student_id, class_id),
    )
    existed = cursor.fetchone()
    if existed:
        cursor.execute(
            """
            UPDATE dangky
            SET id_student_headquarter = %s,
                id_registration_period = %s,
                registration_date = CURRENT_TIMESTAMP,
                status = 'DA_DANG_KY'
            WHERE id_student = %s AND id_class = %s;
            """,
            (student_headquarter, registration_period_id, student_id, class_id),
        )
    else:
        cursor.execute(
            """
            INSERT INTO dangky (id_student, id_student_headquarter, id_class, id_registration_period, status)
            VALUES (%s, %s, %s, %s, 'DA_DANG_KY');
            """,
            (student_id, student_headquarter, class_id, registration_period_id),
        )


def find_student_site(student_id, student_headquarter):
    """Check whether a student exists at the declared student site."""
    conn = None
    try:
        conn = get_connection(student_headquarter)
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1 FROM sinhvien WHERE id = %s;", (student_id,))
            return cursor.fetchone() is not None, "Sinh vien hop le"
    except Exception as exc:
        write_log(f"SITE_DOWN site={student_headquarter} action=KIEM_TRA_SINH_VIEN student={student_id} error={exc}")
        return False, str(exc)
    finally:
        if conn:
            conn.close()


def register_course(student_id, student_headquarter, class_site_code, class_id):
    """Register a class or auto-change group for the same subject/semester/year."""
    if not is_registration_open():
        return False, "Dang ky hoc phan dang dong"

    student_ok, student_message = find_student_site(student_id, student_headquarter)
    if not student_ok:
        return False, f"Khong tim thay sinh vien tai site {student_headquarter}: {student_message}"
    student_info = _get_student_info(student_id, student_headquarter)
    if not student_info:
        return False, "Khong lay duoc thong tin sinh vien"
    student_department, admission_year = student_info

    conn = None
    old_class_id = None
    try:
        conn = get_connection(class_site_code)
        with conn.cursor() as cursor:
            cursor.execute("SET LOCAL lock_timeout = '5s';")
            cursor.execute("SET LOCAL statement_timeout = '10s';")

            target_class = _get_class_metadata(cursor, class_id)
            if target_class is None:
                conn.rollback()
                return False, "Khong tim thay lop hoc phan"

            registration_period = _get_active_registration_period(
                cursor,
                student_department,
                admission_year,
                target_class[1],
                target_class[2],
            )
            if not registration_period:
                conn.rollback()
                return False, "Hien tai chua co dot dang ky hop le cho khoa/khoa hoc cua sinh vien"
            registration_period_id = registration_period[0]

            if not _subject_in_training_program(cursor, student_department, target_class[3]):
                conn.rollback()
                return False, "Hoc phan khong nam trong chuong trinh dao tao cua sinh vien"

            cursor.execute(
                "SELECT pg_advisory_xact_lock(hashtext(%s));",
                (f"{student_id}:{_subject_key(target_class)}",),
            )

            same_subject_class_ids = _find_active_classes_for_same_subject(cursor, student_id, target_class)
            if class_id in same_subject_class_ids:
                conn.rollback()
                return False, "Sinh vien da dang ky lop nay"
            if len(same_subject_class_ids) > 1:
                conn.rollback()
                return False, "Sinh vien dang co nhieu dang ky cung hoc phan, can xu ly thu cong"

            old_class_id = same_subject_class_ids[0] if same_subject_class_ids else None
            class_ids_to_lock = [class_id]
            if old_class_id:
                class_ids_to_lock.append(old_class_id)

            locked_classes = _lock_classes_in_fixed_order(cursor, class_ids_to_lock)
            if locked_classes is None:
                conn.rollback()
                return False, "Khong tim thay du lop hoc phan lien quan"

            target_class = locked_classes[class_id]
            if target_class[1] != registration_period[1] or target_class[2] != registration_period[2]:
                conn.rollback()
                return False, "Lop hoc phan khong thuoc dot dang ky hien tai"
            number_of_student, max_student = target_class[4], target_class[5]
            if number_of_student >= max_student:
                conn.rollback()
                return False, "Lop hoc phan da day"

            _lock_student_active_registrations(cursor, student_id)
            ignored_class_id = old_class_id if old_class_id else class_id
            schedule_conflict = _find_schedule_conflict(
                student_id,
                class_site_code,
                cursor,
                class_id,
                ignored_class_id,
            )
            if schedule_conflict:
                conn.rollback()
                if "error" in schedule_conflict:
                    return False, schedule_conflict["error"]
                conflict = schedule_conflict["conflict"]
                return (
                    False,
                    f"Trung lich hoc voi lop {conflict[0]} ({conflict[1]}) "
                    f"ngay {conflict[2]}, tiet {conflict[3]}-{conflict[4]}",
                )

            if old_class_id:
                cursor.execute(
                    """
                    SELECT status
                    FROM dangky
                    WHERE id_student = %s AND id_class IN (%s, %s)
                    ORDER BY id_class
                    FOR UPDATE;
                    """,
                    (student_id, old_class_id, class_id),
                )
                cursor.fetchall()
                cursor.execute(
                    """
                    UPDATE dangky
                    SET status = 'DA_HUY'
                    WHERE id_student = %s AND id_class = %s;
                    """,
                    (student_id, old_class_id),
                )
                _activate_registration(cursor, student_id, student_headquarter, class_id, registration_period_id)
            else:
                _activate_registration(cursor, student_id, student_headquarter, class_id, registration_period_id)

        conn.commit()
        if old_class_id:
            write_log(
                f"DOI_LOP site={class_site_code} old_class={old_class_id} "
                f"new_class={class_id} student={student_id} success=True"
            )
            return True, "Doi lop hoc phan thanh cong"

        write_log(f"DANG_KY site={class_site_code} class={class_id} student={student_id} success=True")
        return True, "Dang ky hoc phan thanh cong"
    except Exception as exc:
        if conn:
            conn.rollback()
        if conn is None:
            write_log(f"SITE_DOWN site={class_site_code} action=DANG_KY student={student_id} class={class_id} error={exc}")
            return False, f"Khong the ket noi site {class_site_code}, giao dich dang ky bi huy de dam bao nhat quan du lieu"
        write_log(f"DANG_KY site={class_site_code} class={class_id} student={student_id} success=False error={exc}")
        return False, str(exc)
    finally:
        if conn:
            conn.close()


def cancel_registration(student_id, class_site_code, class_id):
    """Cancel a registration using the same class-first lock order."""
    conn = None
    try:
        conn = get_connection(class_site_code)
        with conn.cursor() as cursor:
            cursor.execute("SET LOCAL lock_timeout = '5s';")
            cursor.execute("SET LOCAL statement_timeout = '10s';")
            cursor.execute(
                """
                SELECT id
                FROM lophocphan
                WHERE id = %s
                FOR UPDATE;
                """,
                (class_id,),
            )
            if cursor.fetchone() is None:
                conn.rollback()
                return False, "Khong tim thay lop hoc phan"

            cursor.execute(
                """
                SELECT d.status, ddk.is_open,
                       CURRENT_TIMESTAMP BETWEEN ddk.start_time AND ddk.end_time AS period_active
                FROM dangky d
                JOIN dotdangky ddk ON ddk.id = d.id_registration_period
                WHERE d.id_student = %s AND d.id_class = %s
                FOR UPDATE;
                """,
                (student_id, class_id),
            )
            row = cursor.fetchone()
            if row is None:
                conn.rollback()
                return False, "Khong tim thay dang ky"
            if row[0] == "DA_HUY":
                conn.rollback()
                return False, "Dang ky da duoc huy truoc do"
            if not row[1] or not row[2]:
                conn.rollback()
                return False, "Dot dang ky da dong, khong the huy dang ky"

            cursor.execute(
                "UPDATE dangky SET status = 'DA_HUY' WHERE id_student = %s AND id_class = %s;",
                (student_id, class_id),
            )

        conn.commit()
        write_log(f"HUY_DANG_KY site={class_site_code} class={class_id} student={student_id}")
        return True, "Huy dang ky thanh cong"
    except Exception as exc:
        if conn:
            conn.rollback()
        if conn is None:
            write_log(f"SITE_DOWN site={class_site_code} action=HUY_DANG_KY student={student_id} class={class_id} error={exc}")
            return False, f"Khong the ket noi site {class_site_code}, giao dich huy dang ky bi huy de dam bao nhat quan du lieu"
        return False, str(exc)
    finally:
        if conn:
            conn.close()


def reset_test_class(class_site_code="HL", class_id="LHP-HL-TEST", max_student=1):
    """Reset demo class so the concurrent registration demo can be repeated."""
    if max_student < 1:
        return False, "max_student phai lon hon hoac bang 1"

    conn = None
    try:
        conn = get_connection(class_site_code)
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1 FROM lophocphan WHERE id = %s FOR UPDATE;", (class_id,))
            if cursor.fetchone() is None:
                conn.rollback()
                return False, "Khong tim thay lop hoc phan"

            cursor.execute("DELETE FROM dangky WHERE id_class = %s;", (class_id,))
            cursor.execute(
                """
                UPDATE lophocphan
                SET number_of_student = 0,
                    max_student = %s
                WHERE id = %s;
                """,
                (max_student, class_id),
            )

        conn.commit()
        write_log(f"RESET_LOP_TEST site={class_site_code} class={class_id} max_student={max_student}")
        return True, "Reset lop test thanh cong"
    except Exception as exc:
        if conn:
            conn.rollback()
        write_log(f"RESET_LOP_TEST site={class_site_code} class={class_id} success=False error={exc}")
        return False, str(exc)
    finally:
        if conn:
            conn.close()


def simulate_concurrent_registration(class_site_code, class_id, students):
    """Run multiple registration attempts in parallel threads."""
    results = []
    lock = threading.Lock()

    def worker(student):
        started_at = datetime.now()
        success, message = register_course(
            student["id_student"],
            student["id_student_headquarter"],
            class_site_code,
            class_id,
        )
        with lock:
            results.append(
                {
                    "id_student": student["id_student"],
                    "id_student_headquarter": student["id_student_headquarter"],
                    "class_id": class_id,
                    "success": success,
                    "message": message,
                    "time": started_at.strftime("%Y-%m-%d %H:%M:%S.%f"),
                }
            )

    threads = [threading.Thread(target=worker, args=(student,)) for student in students]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    return pd.DataFrame(results).sort_values("time", ignore_index=True)
