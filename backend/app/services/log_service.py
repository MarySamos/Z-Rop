"""操作日志服务.

记录和查询用户操作日志
"""
from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.db.models import OperationLog, User

# Default query values
_DEFAULT_DAYS = 7
_DEFAULT_LIMIT = 100
_DEFAULT_STATUS = "success"
_STATS_DAYS_DEFAULT = 30
_TOP_USERS_LIMIT = 10


class LogService:
    """操作日志服务"""

    @staticmethod
    def log_action(
        db: Session,
        user_id: int,
        action: str,
        resource: Optional[str] = None,
        details: Optional[str] = None,
        ip_address: Optional[str] = None,
        status: str = _DEFAULT_STATUS,
    ) -> OperationLog:
        """记录操作日志.

        Args:
            db: 数据库会话
            user_id: 用户ID
            action: 操作类型 (login, logout, query, upload, export, etc.)
            resource: 操作资源
            details: 详细信息
            ip_address: IP地址
            status: 状态 (success/failed)
        """
        log = OperationLog(
            user_id=user_id,
            action=action,
            resource=resource,
            details=details,
            ip_address=ip_address,
            status=status,
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log

    @staticmethod
    def get_logs(
        db: Session,
        user_id: Optional[int] = None,
        action: Optional[str] = None,
        days: int = _DEFAULT_DAYS,
        limit: int = _DEFAULT_LIMIT,
    ) -> List[OperationLog]:
        """查询操作日志.

        Args:
            db: 数据库会话
            user_id: 按用户筛选
            action: 按操作类型筛选
            days: 查询最近多少天
            limit: 最大返回条数
        """
        query = db.query(OperationLog)

        since = datetime.utcnow() - timedelta(days=days)
        query = query.filter(OperationLog.created_at >= since)

        if user_id:
            query = query.filter(OperationLog.user_id == user_id)

        if action:
            query = query.filter(OperationLog.action == action)

        return query.order_by(desc(OperationLog.created_at)).limit(limit).all()

    @staticmethod
    def get_stats(db: Session, days: int = _STATS_DAYS_DEFAULT) -> dict:
        """获取日志统计"""
        since = datetime.utcnow() - timedelta(days=days)

        total = db.query(func.count(OperationLog.id)).filter(
            OperationLog.created_at >= since
        ).scalar()

        by_action = db.query(
            OperationLog.action,
            func.count(OperationLog.id),
        ).filter(
            OperationLog.created_at >= since
        ).group_by(OperationLog.action).all()

        by_user = db.query(
            User.name,
            func.count(OperationLog.id),
        ).join(User).filter(
            OperationLog.created_at >= since
        ).group_by(User.name).order_by(
            desc(func.count(OperationLog.id))
        ).limit(_TOP_USERS_LIMIT).all()

        return {
            "total_operations": total,
            "by_action": {action: count for action, count in by_action},
            "top_users": [{"name": name, "count": count} for name, count in by_user],
            "period_days": days,
        }


# 全局服务实例
log_service = LogService()
