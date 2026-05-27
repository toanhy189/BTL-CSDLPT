"""Module phục vụ nghiệp vụ bảo mật trong hệ thống đăng ký học phần phân tán."""

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from backend.core.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    JWT_ALGORITHM,
    JWT_SECRET_KEY,
)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


#  Băm mật khẩu trước khi lưu vào database tài khoản.
def hash_password(password):
    """Băm mật khẩu trước khi lưu vào database tài khoản."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


#  So khớp mật khẩu người dùng nhập với mật khẩu đã băm.
def verify_password(password, password_hash):
    """So khớp mật khẩu người dùng nhập với mật khẩu đã băm."""
    if not password_hash:
        return False
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


#  Tạo JWT chứa thông tin định danh, vai trò và thời hạn đăng nhập.
def create_access_token(data):
    """Tạo JWT chứa thông tin định danh, vai trò và thời hạn đăng nhập."""
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload.update({"exp": expire})
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


#  Giải mã JWT để lấy payload người dùng từ token gửi kèm request.
def decode_access_token(token):
    """Giải mã JWT để lấy payload người dùng từ token gửi kèm request."""
    try:
        return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không hợp lệ hoặc đã hết hạn",
        ) from exc


#  Dependency đọc Bearer token và trả thông tin người dùng hiện tại.
def get_current_user(token=Depends(oauth2_scheme)):
    """Dependency đọc Bearer token và trả thông tin người dùng hiện tại."""
    payload = decode_access_token(token)
    username = payload.get("sub")
    role = payload.get("role")
    if not username or not role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token thiếu thông tin")
    return {
        "username": username,
        "role": role,
        "ref_id": payload.get("ref_id"),
        "id_headquarter": payload.get("id_headquarter"),
        "site_code": payload.get("site_code"),
    }


#  Tạo dependency kiểm tra người dùng có vai trò hợp lệ trước khi vào API.
def require_role(roles):
    """Tạo dependency kiểm tra người dùng có vai trò hợp lệ trước khi vào API."""
    #  Kiểm tra vai trò của request hiện tại trước khi cho phép vào endpoint.
    def dependency(current_user=Depends(get_current_user)):
        """Kiểm tra vai trò của request hiện tại trước khi cho phép vào endpoint."""
        if current_user["role"] not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Không đủ quyền truy cập",
            )
        return current_user

    return dependency
