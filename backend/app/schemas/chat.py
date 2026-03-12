"""聊天相关的 Pydantic 模型.

定义聊天请求和响应的数据格式
"""
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """聊天请求模型"""
    message: str = Field(..., description="用户消息内容")
    session_id: Optional[str] = Field(None, description="会话ID（用于checkpoint记忆）")
    user_id: Optional[str] = Field("default", description="用户ID")
    history: Optional[List[Dict[str, str]]] = Field(default_factory=list, description="聊天历史（保留兼容性）")


class ChatResponse(BaseModel):
    """聊天响应模型"""
    answer: str = Field(..., description="AI 回答")
    chart: Optional[str] = Field(None, description="图表 HTML 代码")
    sql: Optional[str] = Field(None, description="执行的 SQL 语句")
    intent: str = Field(..., description="识别的意图类型")
    session_id: Optional[str] = Field(None, description="会话ID")


class ChatStreamRequest(BaseModel):
    """流式聊天请求模型"""
    message: str = Field(..., description="用户消息内容")
    session_id: Optional[str] = Field(None, description="会话ID（用于checkpoint）")
    user_id: Optional[str] = Field("default", description="用户ID")
