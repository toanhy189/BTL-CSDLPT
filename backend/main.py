"""Điểm khởi động FastAPI, cấu hình CORS, khởi tạo xác thực và gắn các router nghiệp vụ."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api import (
    admin_api,
    auth_api,
    concurrency_api,
    distributed_query_api,
    registration_api,
    student_api,
    teacher_api,
)
from backend.services.auth_service import ensure_auth_schema


app = FastAPI(title="CSDL phân tán - Đăng ký học phần API")

# Cho phép frontend Streamlit gọi API trong lúc chạy local.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",
        "http://127.0.0.1:8501",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Chạy khi backend khởi động để bảo đảm bảng/tài khoản xác thực đã sẵn sàng.
@app.on_event("startup")
def on_startup():
    """Chạy khi backend khởi động để bảo đảm bảng/tài khoản xác thực đã sẵn sàng."""
    ensure_auth_schema()


# Endpoint kiểm tra nhanh backend còn phản hồi.
@app.get("/health")
def health():
    """Endpoint kiểm tra nhanh backend còn phản hồi."""
    return {"status": "ok"}


# Gắn các nhóm API theo vai trò/nghiệp vụ sau khi cấu hình xong app.
app.include_router(auth_api.router)
app.include_router(admin_api.router)
app.include_router(student_api.router)
app.include_router(teacher_api.router)
app.include_router(registration_api.router)
app.include_router(distributed_query_api.router)
app.include_router(concurrency_api.router)
