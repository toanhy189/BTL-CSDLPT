"""Course registration service for the legacy Streamlit app."""

from datetime import datetime
import threading

import pandas as pd

from db.connections import SITE_CODES, get_connection
from backend.core.registration_config import is_registration_open
from services.log_service import write_log


def _subject_key(class_row):
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
            return {"error": f"Khong kiem tra duoc lich hoc tai site {site_code}: {exc}"}
        finally:
            if conn:
                conn.close()
    return None


def _activate_registration(cursor, student_id, student_headquarter, class_id):
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
                registration_date = CURRENT_TIMESTAMP,
                status = 'DA_DANG_KY'
            WHERE id_student = %s AND id_class = %s;
            """,
            (student_headquarter, student_id, class_id),
        )
    else:
        cursor.execute(
            """
            INSERT INTO dangky (id_student, id_student_headquarter, id_class, status)
            VALUES (%s, %s, %s, 'DA_DANG_KY');
            """,
            (student_id, student_headquarter, class_id),
        )


def find_student_site(student_id, student_headquarter):
    conn = None
    try:
        conn = get_connection(student_headquarter)
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1 FROM sinhvien WHERE id = %s;", (student_id,))
            return cursor.fetchone() is not None, "Sinh vien hop le"
    except Exception as exc:
        return False, str(exc)
    finally:
        if conn is not None:
            conn.close()


def register_course(student_id, student_headquarter, class_site_code, class_id):
    if not is_registration_open():
        return False, "Dang ky hoc phan dang dong"

    student_ok, student_message = find_student_site(student_id, student_headquarter)
    if not student_ok:
        return False, f"Khong tim thay sinh vien tai site {student_headquarter}: {student_message}"

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
                _activate_registration(cursor, student_id, student_headquarter, class_id)
            else:
                _activate_registration(cursor, student_id, student_headquarter, class_id)

        conn.commit()
        if old_class_id:
            write_log(
                f"DOI_LOP site={class_site_code} old_class={old_class_id} "
                f"new_class={class_id} student={student_id} success=True"
            )
            return True, "Doi lop hoc phan thanh cong"

        write_log(
            f"DANG_KY site={class_site_code} class={class_id} student={student_id} "
            f"student_site={student_headquarter} success=True"
        )
        return True, "Dang ky hoc phan thanh cong"
    except Exception as exc:
        if conn is not None:
            conn.rollback()
        write_log(
            f"DANG_KY site={class_site_code} class={class_id} student={student_id} "
            f"student_site={student_headquarter} success=False error={exc}"
        )
        return False, str(exc)
    finally:
        if conn is not None:
            conn.close()


def cancel_registration(student_id, class_site_code, class_id):
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
                SELECT status
                FROM dangky
                WHERE id_student = %s AND id_class = %s
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

            cursor.execute(
                """
                UPDATE dangky
                SET status = 'DA_HUY'
                WHERE id_student = %s AND id_class = %s;
                """,
                (student_id, class_id),
            )

        conn.commit()
        write_log(f"HUY_DANG_KY site={class_site_code} class={class_id} student={student_id}")
        return True, "Huy dang ky thanh cong"
    except Exception as exc:
        if conn is not None:
            conn.rollback()
        return False, str(exc)
    finally:
        if conn is not None:
            conn.close()


def simulate_concurrent_registration(class_site_code, class_id, students):
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

    df = pd.DataFrame(results)
    if not df.empty:
        df = df.sort_values("time", ignore_index=True)
    return df
