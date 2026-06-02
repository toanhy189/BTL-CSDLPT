"""Cấu hình mở/đóng đăng ký học phần được lưu bằng file JSON cục bộ."""

from pathlib import Path
import json


CONFIG_PATH = Path(__file__).resolve().parents[2] / "registration_config.json"
DEFAULT_CONFIG = {"registration_open": True}


def get_registration_config():
    """Đọc cấu hình đăng ký từ file JSON cục bộ."""
    if not CONFIG_PATH.exists():
        return dict(DEFAULT_CONFIG)
    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return dict(DEFAULT_CONFIG)
    return {
        "registration_open": bool(data.get("registration_open", DEFAULT_CONFIG["registration_open"])),
    }


def set_registration_open(is_open):
    """Lưu trạng thái mở/đóng đăng ký học phần."""
    data = {"registration_open": bool(is_open)}
    CONFIG_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return data


def is_registration_open():
    """Trả về việc sinh viên hiện có được phép đăng ký hay không."""
    return get_registration_config()["registration_open"]
