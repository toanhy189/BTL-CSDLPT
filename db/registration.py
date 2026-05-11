"""Course registration operations."""

from db.connections import get_connection
from db.logs import write_log


def register_course(site_code, student_id, course_id):
    """Insert one course registration into the selected distributed site."""
    sql = """
        INSERT INTO registrations (student_id, course_id)
        VALUES (%s, %s)
        RETURNING id;
    """
    with get_connection(site_code) as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, (student_id, course_id))
            registration_id = cursor.fetchone()[0]
        conn.commit()

    write_log(
        f"site={site_code} student_id={student_id} "
        f"course_id={course_id} registration_id={registration_id}"
    )
    return registration_id
