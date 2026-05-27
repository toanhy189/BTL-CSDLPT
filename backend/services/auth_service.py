"""Service xác thực: tạo bảng tài khoản, seed tài khoản demo và xử lý đăng nhập."""

from fastapi import HTTPException, status

from backend.core.config import SITE_CODES
from backend.core.security import create_access_token, hash_password, verify_password
from backend.db.connections import get_connection


CREATE_ACCOUNT_SQL = """
CREATE TABLE IF NOT EXISTS taikhoan (
    username varchar(255) PRIMARY KEY,
    password_hash text NOT NULL,
    role varchar(50) NOT NULL,
    ref_id varchar(255),
    id_headquarter varchar(255),
    created_at timestamp DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT CK_TaiKhoan_Role CHECK (role IN ('ADMIN', 'GIANG_VIEN', 'SINH_VIEN'))
);
"""


# Tạo bảng tài khoản nếu thiếu và seed tài khoản demo ban đầu.
def ensure_auth_schema():
    """Tạo bảng tài khoản nếu thiếu và seed tài khoản demo ban đầu."""
    for site_code in SITE_CODES:
        conn = None
        try:
            conn = get_connection(site_code)
            with conn.cursor() as cursor:
                cursor.execute(CREATE_ACCOUNT_SQL)
            conn.commit()
        except Exception as exc:
            print(f"[{site_code}] Không tạo được bảng taikhoan: {exc}")
            if conn:
                conn.rollback()
        finally:
            if conn:
                conn.close()

    _ensure_demo_accounts()


# Thêm tài khoản vào site nếu username chưa tồn tại, mật khẩu luôn được băm trước khi lưu.
def _insert_account(site_code, username, password, role, ref_id=None, id_headquarter=None):
    """Thêm tài khoản vào site nếu username chưa tồn tại, mật khẩu luôn được băm trước khi lưu."""
    conn = get_connection(site_code)
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO taikhoan (username, password_hash, role, ref_id, id_headquarter)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (username) DO NOTHING;
                """,
                (username, hash_password(password), role, ref_id, id_headquarter),
            )
        conn.commit()
    finally:
        conn.close()


# Lấy một mã dữ liệu mẫu từ bảng sinh viên/giảng viên để gắn tài khoản demo.
def _fetch_one_id(site_code, table_name, id_col="id"):
    """Lấy một mã dữ liệu mẫu từ bảng sinh viên/giảng viên để gắn tài khoản demo."""
    conn = get_connection(site_code)
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"SELECT {id_col} FROM {table_name} ORDER BY {id_col} LIMIT 1;")
            row = cursor.fetchone()
            return row[0] if row else None
    finally:
        conn.close()


# Tạo tài khoản demo cho admin, sinh viên và giảng viên dựa trên dữ liệu đang có ở mỗi site.
def _ensure_demo_accounts():
    """Tạo tài khoản demo cho admin, sinh viên và giảng viên dựa trên dữ liệu đang có ở mỗi site."""
    try:
        _insert_account("HL", "admin", "admin123", "ADMIN", "admin", "HL")
    except Exception as exc:
        print(f"Không seed được admin demo: {exc}")

    for site_code in SITE_CODES:
        try:
            student_id = _fetch_one_id(site_code, "sinhvien")
            if student_id:
                _insert_account(
                    site_code,
                    student_id.lower(),
                    "123456",
                    "SINH_VIEN",
                    student_id,
                    site_code,
                )
            teacher_id = _fetch_one_id(site_code, "giangvien")
            if teacher_id:
                _insert_account(
                    site_code,
                    teacher_id.lower(),
                    "123456",
                    "GIANG_VIEN",
                    teacher_id,
                    site_code,
                )
        except Exception as exc:
            print(f"[{site_code}] Không seed được tài khoản demo: {exc}")


# Quét các site để tìm tài khoản theo username vì tài khoản có thể nằm ở site quản lý người dùng.
def find_account(username):
    """Quét các site để tìm tài khoản theo username vì tài khoản có thể nằm ở site quản lý người dùng."""
    for site_code in SITE_CODES:
        conn = None
        try:
            conn = get_connection(site_code)
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT username, password_hash, role, ref_id, id_headquarter
                    FROM taikhoan
                    WHERE username = %s;
                    """,
                    (username,),
                )
                row = cursor.fetchone()
                if row:
                    return {
                        "username": row[0],
                        "password_hash": row[1],
                        "role": row[2],
                        "ref_id": row[3],
                        "id_headquarter": row[4],
                        "site_code": site_code,
                    }
        except Exception as exc:
            print(f"[{site_code}] Lỗi tìm tài khoản: {exc}")
        finally:
            if conn:
                conn.close()
    return None


# Kiểm tra username/password, tạo token và trả thông tin người dùng cho frontend.
def login_user(username, password):
    """Kiểm tra username/password, tạo token và trả thông tin người dùng cho frontend."""
    account = find_account(username)
    if not account or not verify_password(password, account["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tên đăng nhập hoặc mật khẩu không đúng",
        )

    user = {
        "username": account["username"],
        "role": account["role"],
        "ref_id": account["ref_id"],
        "id_headquarter": account["id_headquarter"],
        "site_code": account["site_code"],
    }
    token = create_access_token(
        {
            "sub": user["username"],
            "role": user["role"],
            "ref_id": user["ref_id"],
            "id_headquarter": user["id_headquarter"],
            "site_code": user["site_code"],
        }
    )
    return {"access_token": token, "token_type": "bearer", "user": user}
