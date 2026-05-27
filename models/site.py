"""Mô hình dữ liệu/schema cho nghiệp vụ site."""

from dataclasses import dataclass


# Dataclass biểu diễn một site/cơ sở trong kiến trúc database phân tán.
@dataclass
class Site:
    """Dataclass biểu diễn một site/cơ sở trong kiến trúc database phân tán."""
    code: str
    name: str
    host: str
    port: int
    database: str
