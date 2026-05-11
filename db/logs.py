"""Logging helpers for registration workflows."""

from datetime import datetime
from pathlib import Path


LOG_FILE = Path(__file__).resolve().parents[1] / "logs" / "concurrent_registration_log.txt"


def write_log(message):
    """Append one timestamped line to the concurrent registration log."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with LOG_FILE.open("a", encoding="utf-8") as file:
        file.write(f"[{timestamp}] {message}\n")
