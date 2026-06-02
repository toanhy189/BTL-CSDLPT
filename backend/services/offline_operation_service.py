"""Ghi nhận và xử lý lại yêu cầu bị gián đoạn tại site điều phối HD."""

from psycopg2.extras import Json

from backend.db.connections import check_site_connection
from backend.db.connections import get_connection
from backend.services.log_service import write_log


COORDINATOR_SITE = "HD"
VALID_STATUSES = {"PENDING", "RETRYING", "DONE", "FAILED", "CANCELLED"}


def ensure_offline_operation_schema():
    conn = None
    try:
        conn = get_connection(COORDINATOR_SITE)
        with conn.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS offlineoperationlog (
                    id serial NOT NULL,
                    site_code varchar(10) NOT NULL,
                    action varchar(50) NOT NULL,
                    payload jsonb NOT NULL,
                    error_message text,
                    status varchar(20) NOT NULL DEFAULT 'PENDING',
                    created_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    retried_at timestamp,
                    retry_count int NOT NULL DEFAULT 0,
                    CONSTRAINT pk_offlineoperationlog PRIMARY KEY (id),
                    CONSTRAINT ck_offlineoperationlog_action
                        CHECK (action IN ('DANG_KY', 'HUY_DANG_KY')),
                    CONSTRAINT ck_offlineoperationlog_status
                        CHECK (status IN ('PENDING', 'RETRYING', 'DONE', 'FAILED', 'CANCELLED'))
                );
                """
            )
        conn.commit()
    except Exception as exc:
        if conn:
            conn.rollback()
        write_log(f"OFFLINE_OPERATION_SCHEMA_FAILED site={COORDINATOR_SITE} error={exc}")
    finally:
        if conn:
            conn.close()


def create_offline_operation(site_code, action, payload, error_message):
    """Lưu một thao tác chưa hoàn tất do site tạm thời không khả dụng."""
    conn = None
    try:
        conn = get_connection(COORDINATOR_SITE)
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO offlineoperationlog (site_code, action, payload, error_message)
                VALUES (%s, %s, %s, %s)
                RETURNING id;
                """,
                (site_code, action, Json(payload), error_message),
            )
            operation_id = cursor.fetchone()[0]
        conn.commit()
        write_log(
            f"OFFLINE_OPERATION_CREATE id={operation_id} site={site_code} "
            f"action={action} status=PENDING"
        )
        return operation_id
    except Exception as exc:
        if conn:
            conn.rollback()
        write_log(f"OFFLINE_OPERATION_CREATE_FAILED site={site_code} action={action} error={exc}")
        return None
    finally:
        if conn:
            conn.close()


def list_offline_operations(status=None):
    conn = None
    try:
        conn = get_connection(COORDINATOR_SITE)
        with conn.cursor() as cursor:
            if status:
                cursor.execute(
                    """
                    SELECT id, site_code, action, payload, error_message, status,
                           created_at, retried_at, retry_count
                    FROM offlineoperationlog
                    WHERE status = %s
                    ORDER BY created_at DESC, id DESC;
                    """,
                    (status,),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, site_code, action, payload, error_message, status,
                           created_at, retried_at, retry_count
                    FROM offlineoperationlog
                    ORDER BY created_at DESC, id DESC;
                    """
                )
            rows = cursor.fetchall()
        return [
            {
                "id": row[0],
                "site_code": row[1],
                "action": row[2],
                "payload": row[3],
                "error_message": row[4],
                "status": row[5],
                "created_at": row[6],
                "retried_at": row[7],
                "retry_count": row[8],
            }
            for row in rows
        ]
    finally:
        if conn:
            conn.close()


def update_offline_operation_status(operation_id, status, error_message=None):
    if status not in VALID_STATUSES:
        return False, "Trang thai offline operation khong hop le"

    conn = None
    try:
        conn = get_connection(COORDINATOR_SITE)
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE offlineoperationlog
                SET status = %s,
                    error_message = COALESCE(%s, error_message),
                    retried_at = CASE
                        WHEN %s IN ('RETRYING', 'DONE', 'FAILED') THEN CURRENT_TIMESTAMP
                        ELSE retried_at
                    END
                WHERE id = %s;
                """,
                (status, error_message, status, operation_id),
            )
            if cursor.rowcount == 0:
                conn.rollback()
                return False, "Khong tim thay offline operation"
        conn.commit()
        return True, "Cap nhat trang thai thanh cong"
    except Exception as exc:
        if conn:
            conn.rollback()
        return False, str(exc)
    finally:
        if conn:
            conn.close()


def retry_offline_operation(operation_id):
    from backend.services.registration_service import cancel_registration, register_course

    conn = None
    try:
        conn = get_connection(COORDINATOR_SITE)
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT action, payload, status
                FROM offlineoperationlog
                WHERE id = %s
                FOR UPDATE;
                """,
                (operation_id,),
            )
            row = cursor.fetchone()
            if row is None:
                conn.rollback()
                return False, "Khong tim thay offline operation"
            action, payload, status = row
            if status not in ("PENDING", "FAILED"):
                conn.rollback()
                return False, f"Khong the retry operation dang o trang thai {status}"

            cursor.execute(
                """
                UPDATE offlineoperationlog
                SET status = 'RETRYING',
                    retry_count = retry_count + 1,
                    retried_at = CURRENT_TIMESTAMP
                WHERE id = %s;
                """,
                (operation_id,),
            )
        conn.commit()
    except Exception as exc:
        if conn:
            conn.rollback()
        return False, str(exc)
    finally:
        if conn:
            conn.close()

    if action == "DANG_KY":
        success, message = register_course(
            payload["student_id"],
            payload["student_headquarter"],
            payload["class_site_code"],
            payload["class_id"],
            capture_offline=False,
        )
    elif action == "HUY_DANG_KY":
        success, message = cancel_registration(
            payload["student_id"],
            payload["class_site_code"],
            payload["class_id"],
            capture_offline=False,
        )
    else:
        success, message = False, f"Action khong ho tro retry: {action}"

    final_status = "DONE" if success else "FAILED"
    update_offline_operation_status(operation_id, final_status, message)
    write_log(
        f"OFFLINE_OPERATION_RETRY id={operation_id} action={action} "
        f"success={success} message={message}"
    )
    return success, message


def retry_all_pending_operations():
    operations = [
        row
        for row in list_offline_operations()
        if row["status"] in ("PENDING", "FAILED")
    ]
    summary = {
        "total": len(operations),
        "retried": 0,
        "done": 0,
        "failed": 0,
        "skipped": 0,
        "items": [],
    }

    site_status_cache = {}
    for operation in operations:
        site_code = operation["site_code"]
        if site_code not in site_status_cache:
            site_status_cache[site_code] = check_site_connection(site_code)
        site_ok, site_message = site_status_cache[site_code]
        if not site_ok:
            summary["skipped"] += 1
            summary["items"].append(
                {
                    "id": operation["id"],
                    "site_code": site_code,
                    "success": False,
                    "skipped": True,
                    "message": f"Site {site_code} chua ket noi lai: {site_message}",
                }
            )
            continue

        summary["retried"] += 1
        success, message = retry_offline_operation(operation["id"])
        if success:
            summary["done"] += 1
        else:
            summary["failed"] += 1
        summary["items"].append(
            {
                "id": operation["id"],
                "site_code": site_code,
                "success": success,
                "skipped": False,
                "message": message,
            }
        )

    write_log(
        "OFFLINE_OPERATION_RETRY_ALL "
        f"total={summary['total']} retried={summary['retried']} "
        f"done={summary['done']} failed={summary['failed']} skipped={summary['skipped']}"
    )
    return summary
