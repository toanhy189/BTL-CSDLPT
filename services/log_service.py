"""Ghi va doc log thao tac demo."""

from datetime import datetime
from pathlib import Path

import pandas as pd


LOG_FILE = Path("logs") / "concurrent_registration_log.txt"


def write_log(message):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with LOG_FILE.open("a", encoding="utf-8") as file:
        file.write(f"[{timestamp}] {message}\n")


def write_concurrent_result(df):
    if df is None or df.empty:
        write_log("Mo phong dong thoi: khong co ket qua")
        return
    success_count = int(df["success"].sum()) if "success" in df else 0
    write_log(f"Mo phong dong thoi: {success_count}/{len(df)} thanh cong")
    with LOG_FILE.open("a", encoding="utf-8") as file:
        file.write(df.to_string(index=False))
        file.write("\n")


def read_logs():
    if not LOG_FILE.exists():
        return ""
    return LOG_FILE.read_text(encoding="utf-8")


def read_log_lines(limit=200):
    content = read_logs()
    if not content:
        return []
    return content.splitlines()[-limit:]
