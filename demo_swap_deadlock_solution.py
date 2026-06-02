"""Demo hai sinh viên đổi lớp chéo cùng lúc bằng service đăng ký thật.



File này không viết lại logic đăng ký/đổi lớp. Phần nghiệp vụ thật vẫn nằm ở
register_course() trong backend/services/registration_service.py.

Script chỉ làm thêm 2 việc để demo chạy chắc chắn:
1. Chuẩn bị dữ liệu: tạo 2 lớp demo cùng học phần và gán mỗi sinh viên vào 1 lớp.
2. Tạo 2 thread gọi register_course() cùng lúc để đổi lớp chéo.

Kết quả mong đợi: cả 2 thread xử lý xong mà không có lỗi "deadlock detected",
vì register_course() đã khóa các lớp liên quan theo thứ tự cố định.
"""

from datetime import datetime
import threading

from backend.db.connections import get_connection
from backend.services.registration_service import register_course


SITE_CODE = "HL"
CLASS_A = "LHP-HL-SWAP-A"
CLASS_B = "LHP-HL-SWAP-B"
SEMESTER = 2
SCHOOL_YEAR = 2026


def _fetchone_required(cursor, sql, params=None, message="Required demo data was not found"):
    """Lấy một dòng bắt buộc; nếu không có thì dừng demo với thông báo rõ ràng."""
    cursor.execute(sql, params or ())
    row = cursor.fetchone()
    if row is None:
        raise RuntimeError(message)
    return row


def prepare_demo_data():
    """Chuẩn bị kịch bản đổi lớp chéo có thể chạy lặp lại nhiều lần.

    Các câu SELECT/INSERT/UPDATE trong hàm này chỉ dùng để setup dữ liệu demo.
    Logic đăng ký/đổi lớp thật không nằm ở đây, mà nằm trong register_course().
    """
    conn = get_connection(SITE_CODE)
    try:
        with conn.cursor() as cursor:
            # Chọn 2 sinh viên cùng khoa và cùng năm nhập học để dùng cùng đợt đăng ký.
            student_dept, admission_year = _fetchone_required(
                cursor,
                """
                SELECT id_department, year_of_admission
                FROM sinhvien
                WHERE id_headquarter = %s
                GROUP BY id_department, year_of_admission
                HAVING COUNT(*) >= 2
                ORDER BY id_department, year_of_admission
                LIMIT 1;
                """,
                (SITE_CODE,),
                "Need at least two HL students in the same department and admission year",
            )

            # Lấy chính xác 2 sinh viên sẽ tham gia đổi lớp chéo.
            cursor.execute(
                """
                SELECT id
                FROM sinhvien
                WHERE id_headquarter = %s
                  AND id_department = %s
                  AND year_of_admission = %s
                ORDER BY id
                LIMIT 2;
                """,
                (SITE_CODE, student_dept, admission_year),
            )
            student_a, student_b = [row[0] for row in cursor.fetchall()]

            # Chọn một học phần thuộc chương trình đào tạo của khoa đó.
            # Như vậy register_course() sẽ không bị fail vì học phần không hợp lệ.
            subject_id = _fetchone_required(
                cursor,
                """
                SELECT ctdt.id_subject
                FROM chuongtrinhdaotao ctdt
                JOIN hocphan hp ON hp.id = ctdt.id_subject
                WHERE ctdt.id_department = %s
                ORDER BY ctdt.id_subject
                LIMIT 1;
                """,
                (student_dept,),
                f"Need a training-program subject for department {student_dept}",
            )[0]

            # Lấy đợt đăng ký đang mở, cùng kỳ/năm học với 2 lớp demo.
            registration_period_id = _fetchone_required(
                cursor,
                """
                SELECT id
                FROM dotdangky
                WHERE id_department = %s
                  AND admission_year = %s
                  AND semester = %s
                  AND school_year = %s
                  AND is_open = true
                  AND CURRENT_TIMESTAMP BETWEEN start_time AND end_time
                ORDER BY id
                LIMIT 1;
                """,
                (student_dept, admission_year, SEMESTER, SCHOOL_YEAR),
                "Need an open registration period for the selected students",
            )[0]

            # Cần một giảng viên hợp lệ để tạo lớp học phần demo.
            teacher_id = _fetchone_required(
                cursor,
                """
                SELECT id
                FROM giangvien
                WHERE id_headquarter = %s
                ORDER BY id
                LIMIT 1;
                """,
                (SITE_CODE,),
                "Need at least one HL teacher",
            )[0]

            # Tạo/cập nhật 2 lớp demo cùng học phần, cùng học kỳ, cùng năm học.
            # Điều kiện này bắt buộc để register_course() hiểu đây là "đổi lớp".
            for class_id in (CLASS_A, CLASS_B):
                cursor.execute(
                    """
                    INSERT INTO lophocphan (
                        id, semester, school_year, number_of_student,
                        max_student, id_subject, id_teacher, id_headquarter
                    )
                    VALUES (%s, %s, %s, 0, 10, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE
                    SET semester = EXCLUDED.semester,
                        school_year = EXCLUDED.school_year,
                        max_student = EXCLUDED.max_student,
                        id_subject = EXCLUDED.id_subject,
                        id_teacher = EXCLUDED.id_teacher,
                        id_headquarter = EXCLUDED.id_headquarter;
                    """,
                    (class_id, SEMESTER, SCHOOL_YEAR, subject_id, teacher_id, SITE_CODE),
                )

            # Xóa các đăng ký cũ của 2 sinh viên trong cùng học phần demo,
            # để mỗi lần chạy script đều quay về một trạng thái ban đầu sạch.
            cursor.execute(
                """
                DELETE FROM dangky d
                USING lophocphan lhp
                WHERE d.id_class = lhp.id
                  AND d.id_student IN (%s, %s)
                  AND lhp.id_subject = %s
                  AND lhp.semester = %s
                  AND lhp.school_year = %s;
                """,
                (student_a, student_b, subject_id, SEMESTER, SCHOOL_YEAR),
            )

            # Reset sĩ số 2 lớp demo. Trigger sẽ tăng lại sĩ số khi insert đăng ký bên dưới.
            cursor.execute(
                """
                UPDATE lophocphan
                SET number_of_student = 0,
                    max_student = 10
                WHERE id IN (%s, %s);
                """,
                (CLASS_A, CLASS_B),
            )

            # Đặt trạng thái ban đầu:
            # - student_a đang ở lớp A
            # - student_b đang ở lớp B
            # Sau đó 2 thread sẽ gọi register_course() để đổi ngược lại.
            cursor.execute(
                """
                INSERT INTO dangky (
                    id_student, id_student_headquarter, id_class,
                    id_registration_period, status
                )
                VALUES
                    (%s, %s, %s, %s, 'DA_DANG_KY'),
                    (%s, %s, %s, %s, 'DA_DANG_KY');
                """,
                (
                    student_a,
                    SITE_CODE,
                    CLASS_A,
                    registration_period_id,
                    student_b,
                    SITE_CODE,
                    CLASS_B,
                    registration_period_id,
                ),
            )

        conn.commit()
        return student_a, student_b, subject_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def print_current_state(title):
    """In trạng thái 2 lớp demo trước/sau khi đổi lớp để dễ thuyết trình."""
    conn = get_connection(SITE_CODE)
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT d.id_student, d.id_class, d.status, lhp.number_of_student, lhp.max_student
                FROM dangky d
                JOIN lophocphan lhp ON lhp.id = d.id_class
                WHERE d.id_class IN (%s, %s)
                ORDER BY d.id_student, d.id_class;
                """,
                (CLASS_A, CLASS_B),
            )
            print(f"\n{title}")
            for row in cursor.fetchall():
                print(row)
    finally:
        conn.close()


def run_swap(student_id, target_class, results, lock):
    """Hàm chạy trong mỗi thread.

    Đây là phần quan trọng nhất của demo: mỗi thread chỉ gọi hàm đăng ký có sẵn.
    Nếu sinh viên đã đăng ký lớp khác cùng học phần, register_course() sẽ tự xử lý
    thành nghiệp vụ đổi lớp.
    """
    started_at = datetime.now()
    success, message = register_course(student_id, SITE_CODE, SITE_CODE, target_class)
    with lock:
        results.append(
            {
                "student_id": student_id,
                "target_class": target_class,
                "success": success,
                "message": message,
                "started_at": started_at.strftime("%H:%M:%S.%f"),
            }
        )


def main():
    student_a, student_b, subject_id = prepare_demo_data()
    print(f"Demo subject: {subject_id}")
    print(f"{student_a}: {CLASS_A} -> {CLASS_B}")
    print(f"{student_b}: {CLASS_B} -> {CLASS_A}")
    print_current_state("Before concurrent swap")

    results = []
    result_lock = threading.Lock()

    # Tạo 2 luồng đổi lớp chéo:
    # - student_a: lớp A -> lớp B
    # - student_b: lớp B -> lớp A
    # Đây là tình huống dễ gây deadlock nếu service khóa "lớp cũ rồi lớp mới"
    # theo thứ tự khác nhau. register_course() tránh lỗi này bằng cách khóa
    # các lớp liên quan theo thứ tự ID cố định.
    threads = [
        threading.Thread(target=run_swap, args=(student_a, CLASS_B, results, result_lock)),
        threading.Thread(target=run_swap, args=(student_b, CLASS_A, results, result_lock)),
    ]

    # start() gần như cùng lúc để mô phỏng 2 request đổi lớp đồng thời.
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    print("\nConcurrent swap results")
    for row in sorted(results, key=lambda item: item["started_at"]):
        print(row)

    print_current_state("After concurrent swap")


if __name__ == "__main__":
    main()
