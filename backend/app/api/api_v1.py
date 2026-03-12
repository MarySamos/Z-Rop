"""API Routes Aggregation.

集中管理所有 API 路由
"""
from fastapi import APIRouter

from app.api.endpoints import (
    admin,
    analysis,
    auth,
    bigdata,
    chat,
    chat_stream,
    dashboard,
    data_mgmt,
    logs,
    predict,
)

# Create API v1 router
api_router = APIRouter(prefix="/api/v1")

# Register module routers
api_router.include_router(auth.router, tags=["认证"])
api_router.include_router(chat.router, prefix="/chat", tags=["智能对话"])
api_router.include_router(chat_stream.router, prefix="/chat", tags=["智能对话-流式"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["仪表盘"])
api_router.include_router(data_mgmt.router, prefix="/data", tags=["数据管理"])
api_router.include_router(predict.router, prefix="/predict", tags=["ML预测"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["数据分析"])
api_router.include_router(logs.router, prefix="/logs", tags=["操作日志"])
api_router.include_router(bigdata.router, prefix="/bigdata", tags=["大数据实验室"])
api_router.include_router(admin.router, prefix="/admin", tags=["管理员"])

