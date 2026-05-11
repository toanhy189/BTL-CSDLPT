"""Nghiep vu dang ky, huy dang ky va mo phong dong thoi."""

from datetime import datetime
import threading

import pandas as pd

from db.connections import get_connection
from services.log_service import write_log


def find_student_site(student_id, student_headquarter):
    """Kiem tra sinh vien ton tai tai site goc cua sinh vien."""
    conn = None
    try:
        conn = get_connection(student_headquarter)
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1 FROM sinhvien WHERE id = %s;", (student_id,))
            return cursor.fetchone() is not None, "Sinh viên hợp lệ"
    except Exception as exc:
        return False, str(exc)
    finally:
        if conn is not None:
            conn.close()


def register_course(student_id, student_headquarter, class_site_code, class_id):
    """Dang ky hoc phan tai site mo lop, khoa dong lop bang FOR UPDATE."""
    student_ok, student_message = find_student_site(student_id, student_headquarter)
    if not student_ok:
        return False, f"Không tìm thấy sinh viên tại site {student_headquarter}: {student_message}"

    conn = None
    try:
        conn = get_connection(class_site_code)
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT number_of_student, max_student
                FROM lophocphan
                WHERE id = %s
                FOR UPDATE;
                """,
                (class_id,),
            )
            class_row = cursor.fetchone()
            if class_row is None:
                conn.rollback()
                return False, "Không tìm thấy lớp học phần"

            number_of_student, max_student = class_row
            if number_of_student >= max_student:
                conn.rollback()
                return False, "Lớp học phần đã đầy"

            cursor.execute(
                """
                SELECT status
                FROM dangky
                WHERE id_student = %s AND id_class = %s
                FOR UPDATE;
                """,
                (student_id, class_id),
            )
            registration_row = cursor.fetchone()
            if registration_row and registration_row[0] == "DA_DANG_KY":
                conn.rollback()
                return False, "Sinh viên đã đăng ký lớp này"

            if registration_row:
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
                    INSERT INTO dangky (
                        id_student, id_student_headquarter, id_class, status
                    )
                    VALUES (%s, %s, %s, 'DA_DANG_KY');
                    """,
                    (student_id, student_headquarter, class_id),
                )

            cursor.execute(
                """
                UPDATE lophocphan
                SET number_of_student = number_of_student + 1
                WHERE id = %s;
                """,
                (class_id,),
            )

        conn.commit()
        message = "Đăng ký học phần thành công"
        write_log(
            f"DANG_KY site={class_site_code} class={class_id} student={student_id} "
            f"student_site={student_headquarter} success=True"
        )
        return True, message
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
    """Huy dang ky va giam si so neu dang ky dang active."""
    conn = None
    try:
        conn = get_connection(class_site_code)
        with conn.cursor() as cursor:
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
                return False, "Không tìm thấy đăng ký"
            if row[0] == "DA_HUY":
                conn.rollback()
                return False, "Đăng ký đã được hủy trước đó"

            cursor.execute(
                """
                UPDATE dangky
                SET status = 'DA_HUY'
                WHERE id_student = %s AND id_class = %s;
                """,
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
        return True, "Hủy đăng ký thành công"
    except Exception as exc:
        if conn is not None:
            conn.rollback()
        return False, str(exc)
    finally:
        if conn is not None:
            conn.close()


def simulate_concurrent_registration(class_site_code, class_id, students):
    """Chay nhieu thread dang ky cung mot lop de demo khoa dong."""
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
