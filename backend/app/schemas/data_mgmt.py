"""
数据管理相关的 Pydantic 模型
从 common 导入通用模型，保持一致性
"""
from app.schemas.common import TableInfo, DataPage, MessageResponse

__all__ = ["TableInfo", "DataPage", "MessageResponse"]
