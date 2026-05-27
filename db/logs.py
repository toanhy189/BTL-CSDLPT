"""Tầng truy cập dữ liệu cho nghiệp vụ nhật ký, thực hiện đọc/ghi PostgreSQL theo site."""

from datetime import datetime
from pathlib import Path


LOG_FILE = Path(__file__).resolve().parents[1] / "logs" / "concurrent_registration_log.txt"


# Xử lý bước nghiệp vụ nhật ký trong module này.
def write_log(message):
    """Xử lý bước nghiệp vụ nhật ký trong module này."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with LOG_FILE.open("a", encoding="utf-8") as file:
        file.write(f"[{timestamp}] {message}\n")
