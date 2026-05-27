"""Course registration service with row locks and concurrent registration demo."""

from datetime import datetime
import threading

import pandas as pd

from backend.db.connections import get_connection
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
    """Check whether a student exists at the declared student site."""
    conn = None
    try:
        conn = get_connection(student_headquarter)
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1 FROM sinhvien WHERE id = %s;", (student_id,))
            return cursor.fetchone() is not None, "Sinh vien hop le"
    except Exception as exc:
        return False, str(exc)
    finally:
        if conn:
            conn.close()


def register_course(student_id, student_headquarter, class_site_code, class_id):
    """Register a class or auto-change group for the same subject/semester/year."""
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
                cursor.execute(
                    """
                    UPDATE lophocphan
                    SET number_of_student = number_of_student - 1
                    WHERE id = %s AND number_of_student > 0;
                    """,
                    (old_class_id,),
                )
            else:
                _activate_registration(cursor, student_id, student_headquarter, class_id)

            cursor.execute(
                """
                UPDATE lophocphan
                SET number_of_student = number_of_student + 1
                WHERE id = %s;
                """,
                (class_id,),
            )

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
                "UPDATE dangky SET status = 'DA_HUY' WHERE id_student = %s AND id_class = %s;",
                (student_id, class_id),
            )
            cursor.execute(
                """
                UPDATE lophocphan
                SET number_of_student = number_of_student - 1
                WHERE id = %s AND number_of_student > 0;
                """,
                (class_id,),
            )

        conn.commit()
        write_log(f"HUY_DANG_KY site={class_site_code} class={class_id} student={student_id}")
        return True, "Huy dang ky thanh cong"
    except Exception as exc:
        if conn:
            conn.rollback()
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
