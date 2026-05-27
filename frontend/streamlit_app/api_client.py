"""HTTP client để Streamlit frontend gọi FastAPI và chuẩn hóa lỗi trả về."""

import requests


API_BASE_URL = "http://localhost:8000"


# Tạo HTTP header và gắn Bearer token khi người dùng đã đăng nhập.
def _headers(token=None):
    """Tạo HTTP header và gắn Bearer token khi người dùng đã đăng nhập."""
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


# Chuẩn hóa phản hồi API thành dữ liệu hoặc lỗi để các trang UI xử lý thống nhất.
def _handle_response(response):
    """Chuẩn hóa phản hồi API thành dữ liệu hoặc lỗi để các trang UI xử lý thống nhất."""
    try:
        data = response.json()
    except ValueError:
        data = {"detail": response.text}

    if response.status_code >= 400:
        detail = data.get("detail", data)
        return {"_error": True, "status_code": response.status_code, "message": detail}
    return data


# Gọi API GET từ Streamlit và bắt lỗi kết nối hoặc timeout.
def api_get(path, token=None, params=None):
    """Gọi API GET từ Streamlit và bắt lỗi kết nối hoặc timeout."""
    try:
        response = requests.get(
            f"{API_BASE_URL}{path}",
            headers=_headers(token),
            params=params,
            timeout=30,
        )
        return _handle_response(response)
    except requests.RequestException as exc:
        return {"_error": True, "message": str(exc)}


# Gọi API POST từ Streamlit và bắt lỗi kết nối hoặc timeout.
def api_post(path, token=None, json=None, params=None):
    """Gọi API POST từ Streamlit và bắt lỗi kết nối hoặc timeout."""
    try:
        response = requests.post(
            f"{API_BASE_URL}{path}",
            headers=_headers(token),
            params=params,
            json=json,
            timeout=30,
        )
        return _handle_response(response)
    except requests.RequestException as exc:
        return {"_error": True, "message": str(exc)}
