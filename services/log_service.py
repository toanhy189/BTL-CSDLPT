"""Module phục vụ nghiệp vụ nhật ký service trong hệ thống đăng ký học phần phân tán."""

from datetime import datetime
from pathlib import Path

import pandas as pd


LOG_FILE = Path("logs") / "concurrent_registration_log.txt"


# Xử lý bước nghiệp vụ nhật ký trong module này.
def write_log(message):
    """Xử lý bước nghiệp vụ nhật ký trong module này."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with LOG_FILE.open("a", encoding="utf-8") as file:
        file.write(f"[{timestamp}] {message}\n")


# Xử lý bước nghiệp vụ đồng thời result trong module này.
def write_concurrent_result(df):
    """Xử lý bước nghiệp vụ đồng thời result trong module này."""
    if df is None or df.empty:
        write_log("Mo phong dong thoi: khong co ket qua")
        return
    success_count = int(df["success"].sum()) if "success" in df else 0
    write_log(f"Mo phong dong thoi: {success_count}/{len(df)} thanh cong")
    with LOG_FILE.open("a", encoding="utf-8") as file:
        file.write(df.to_string(index=False))
        file.write("\n")


# Lấy dữ liệu nhật ký từ nguồn phù hợp để trả về cho tầng gọi phía trên.
def read_logs():
    """Lấy dữ liệu nhật ký từ nguồn phù hợp để trả về cho tầng gọi phía trên."""
    if not LOG_FILE.exists():
        return ""
    return LOG_FILE.read_text(encoding="utf-8")


# Lấy dữ liệu nhật ký lines từ nguồn phù hợp để trả về cho tầng gọi phía trên.
def read_log_lines(limit=200):
    """Lấy dữ liệu nhật ký lines từ nguồn phù hợp để trả về cho tầng gọi phía trên."""
    content = read_logs()
    if not content:
        return []
    return content.splitlines()[-limit:]
