"""日志相关的 Pydantic 模型.

定义操作日志的数据格式
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class LogResponse(BaseModel):
    """日志响应模型"""
    id: int
    user_id: int
    user_name: Optional[str] = None
    action: str
    resource: Optional[str] = None
    details: Optional[str] = None
    ip_address: Optional[str] = None
    status: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
