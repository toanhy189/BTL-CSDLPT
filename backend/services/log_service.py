"""Service nghiệp vụ nhật ký service, gom xử lý trung gian giữa API và tầng database."""

from datetime import datetime
from pathlib import Path


LOG_FILE = Path("logs") / "concurrent_registration_log.txt"


# Xử lý bước nghiệp vụ nhật ký trong module này.
def write_log(message):
    """Xử lý bước nghiệp vụ nhật ký trong module này."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with LOG_FILE.open("a", encoding="utf-8") as file:
        file.write(f"[{timestamp}] {message}\n")


# Lấy dữ liệu nhật ký từ nguồn phù hợp để trả về cho tầng gọi phía trên.
def read_logs(limit=None):
    """Lấy dữ liệu nhật ký từ nguồn phù hợp để trả về cho tầng gọi phía trên."""
    if not LOG_FILE.exists():
        return ""
    lines = LOG_FILE.read_text(encoding="utf-8").splitlines()
    if limit:
        lines = lines[-limit:]
    return "\n".join(lines)
