"""通用 Pydantic 模型.

定义通用的数据格式
"""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class TableInfo(BaseModel):
    """数据表信息"""
    name: str = Field(..., description="表名")
    row_count: int = Field(..., description="行数")
    columns: List[str] = Field(..., description="列名列表")


class DataPage(BaseModel):
    """分页数据"""
    data: List[Dict[str, Any]] = Field(..., description="数据列表")
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页大小")
    total_pages: int = Field(..., description="总页数")
    columns: List[str] = Field(..., description="列名列表")


class MessageResponse(BaseModel):
    """通用消息响应"""
    message: str = Field(..., description="响应消息")
    success: bool = Field(True, description="是否成功")
    data: Optional[Any] = Field(None, description="附加数据")
