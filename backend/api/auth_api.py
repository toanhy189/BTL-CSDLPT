"""Bộ định tuyến FastAPI cho nhóm nghiệp vụ xác thực, nhận yêu cầu và chuyển xuống service phù hợp."""

from fastapi import APIRouter, Depends

from backend.core.security import get_current_user
from backend.models.schemas import LoginRequest
from backend.services.auth_service import login_user


router = APIRouter(prefix="/auth", tags=["auth"])


# Xác thực username/password và trả token cùng thông tin vai trò.
@router.post("/login")
def login(payload: LoginRequest):
    return login_user(payload.username, payload.password)


# Trả thông tin người dùng hiện tại lấy từ JWT đã xác thực.
@router.get("/me")
def me(current_user=Depends(get_current_user)):
    return current_user
