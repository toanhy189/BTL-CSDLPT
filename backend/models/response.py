"""Schema phản hồi chuẩn để API có cùng cấu trúc trả về."""

from pydantic import BaseModel


# Schema phản hồi chung để API trả trạng thái và thông điệp nhất quán.
class ApiResponse(BaseModel):
    """Schema phản hồi chung để API trả trạng thái và thông điệp nhất quán."""
    success: bool = True
    message: str = "OK"
    data: object | None = None
