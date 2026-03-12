"""操作日志 API 接口"""
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, require_admin
from app.core.database import get_db
from app.db.models import User
from app.services.log_service import log_service

router = APIRouter()

# Query defaults
_DAYS_DEFAULT = 7
_DAYS_MIN = 1
_DAYS_MAX = 90
_LIMIT_DEFAULT = 100
_LIMIT_MIN = 10
_LIMIT_MAX = 500

_MY_LOGS_DAYS_MAX = 30
_MY_LOGS_LIMIT_DEFAULT = 50

_STATS_DAYS_DEFAULT = 30


def _log_to_dict(log, user_name: Optional[str] = None) -> dict:
    """将日志对象转换为字典"""
    return {
        "id": log.id,
        "user_id": log.user_id,
        "user_name": user_name,
        "action": log.action,
        "resource": log.resource,
        "details": log.details,
        "ip_address": log.ip_address,
        "status": log.status,
        "created_at": log.created_at,
    }


@router.get("/list")
async def get_logs(
    user_id: Optional[int] = Query(default=None),
    action: Optional[str] = Query(default=None),
    days: int = Query(default=_DAYS_DEFAULT, ge=_DAYS_MIN, le=_DAYS_MAX),
    limit: int = Query(default=_LIMIT_DEFAULT, ge=_LIMIT_MIN, le=_LIMIT_MAX),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """查询操作日志（管理员专用）"""
    logs = log_service.get_logs(db, user_id=user_id, action=action, days=days, limit=limit)

    result = []
    for log in logs:
        result.append(_log_to_dict(log, log.user.name if log.user else None))

    return result


@router.get("/my")
async def get_my_logs(
    days: int = Query(default=_DAYS_DEFAULT, ge=_DAYS_MIN, le=_MY_LOGS_DAYS_MAX),
    limit: int = Query(default=_MY_LOGS_LIMIT_DEFAULT, ge=_LIMIT_MIN, le=_LIMIT_MAX),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """查询当前用户的操作日志"""
    logs = log_service.get_logs(db, user_id=current_user.id, days=days, limit=limit)

    result = [_log_to_dict(log, current_user.name) for log in logs]
    return result


@router.get("/stats")
async def get_log_stats(
    days: int = Query(default=_STATS_DAYS_DEFAULT, ge=_DAYS_MIN, le=_DAYS_MAX),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """获取日志统计（管理员专用）"""
    return log_service.get_stats(db, days=days)
