"""管理员业务逻辑服务.

提供用户管理和系统概览的业务逻辑
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.db.models import OperationLog, User
from app.services.user_service import hash_password

logger = logging.getLogger(__name__)

# 角色常量
_ROLE_USER = "user"
_ROLE_ADMIN = "admin"
_ROLE_ANALYST = "analyst"

# 查询默认值
_DEFAULT_PAGE = 1
_DEFAULT_PAGE_SIZE = 20
_ACTIVITY_DAYS = 7
_DASHBOARD_LOG_LIMIT = 10
_DASHBOARD_STATS_DAYS = 30


class AdminService:
    """管理员业务逻辑服务"""

    @staticmethod
    def get_all_users(
        db: Session,
        page: int = _DEFAULT_PAGE,
        page_size: int = _DEFAULT_PAGE_SIZE,
        role: Optional[str] = None,
        keyword: Optional[str] = None,
    ) -> dict:
        """获取用户列表（分页 + 筛选）.

        Args:
            db: 数据库会话
            page: 页码（从 1 开始）
            page_size: 每页数量
            role: 按角色筛选
            keyword: 按姓名或工号搜索

        Returns:
            包含 users, total, page, page_size 的字典
        """
        query = db.query(User)

        # 角色筛选
        if role:
            query = query.filter(User.role == role)

        # 关键词搜索（姓名或工号）
        if keyword:
            search_pattern = f"%{keyword}%"
            query = query.filter(
                (User.name.ilike(search_pattern)) | (User.employee_id.ilike(search_pattern))
            )

        # 统计总数
        total = query.count()

        # 分页查询
        offset = (page - 1) * page_size
        users = query.order_by(desc(User.created_at)).offset(offset).limit(page_size).all()

        # 转换用户数据
        user_list = []
        for u in users:
            user_list.append({
                "id": u.id,
                "employee_id": u.employee_id,
                "name": u.name,
                "department": u.department,
                "role": u.role,
                "is_active": u.is_active,
                "created_at": u.created_at.isoformat() if u.created_at else None,
            })

        return {
            "users": user_list,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    @staticmethod
    def update_user_role(db: Session, user_id: int, new_role: str) -> dict:
        """修改用户角色.

        Args:
            db: 数据库会话
            user_id: 用户ID
            new_role: 新角色

        Returns:
            包含操作结果的字典

        Raises:
            ValueError: 如果用户不存在
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"用户 ID {user_id} 不存在")

        old_role = user.role
        user.role = new_role
        db.commit()
        db.refresh(user)

        logger.info("用户 %s 角色从 %s 变更为 %s", user.name, old_role, new_role)

        return {
            "message": f"用户 {user.name} 角色已更新为 {new_role}",
            "user_id": user_id,
            "old_role": old_role,
            "new_role": new_role,
        }

    @staticmethod
    def update_user_status(db: Session, user_id: int, is_active: bool) -> dict:
        """启用/禁用用户.

        Args:
            db: 数据库会话
            user_id: 用户ID
            is_active: 是否激活

        Returns:
            包含操作结果的字典

        Raises:
            ValueError: 如果用户不存在
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"用户 ID {user_id} 不存在")

        user.is_active = is_active
        db.commit()
        db.refresh(user)

        status_text = "启用" if is_active else "禁用"
        logger.info("用户 %s 已被%s", user.name, status_text)

        return {
            "message": f"用户 {user.name} 已{status_text}",
            "user_id": user_id,
            "is_active": is_active,
        }

    @staticmethod
    def create_user_by_admin(
        db: Session,
        employee_id: str,
        name: str,
        password: str,
        department: Optional[str] = None,
        role: str = _ROLE_USER,
    ) -> dict:
        """管理员创建用户.

        Args:
            db: 数据库会话
            employee_id: 工号
            name: 姓名
            password: 密码
            department: 部门
            role: 角色

        Returns:
            创建的用户信息

        Raises:
            ValueError: 如果工号已存在
        """
        # 检查工号是否已存在
        existing = db.query(User).filter(User.employee_id == employee_id).first()
        if existing:
            raise ValueError(f"工号 {employee_id} 已存在")

        hashed_pwd = hash_password(password)
        new_user = User(
            employee_id=employee_id,
            name=name,
            department=department,
            hashed_password=hashed_pwd,
            role=role,
            is_active=True,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        logger.info("管理员创建用户: %s (%s), 角色: %s", name, employee_id, role)

        return {
            "id": new_user.id,
            "employee_id": new_user.employee_id,
            "name": new_user.name,
            "department": new_user.department,
            "role": new_user.role,
            "is_active": new_user.is_active,
            "created_at": new_user.created_at.isoformat() if new_user.created_at else None,
        }

    @staticmethod
    def get_admin_dashboard(db: Session) -> dict:
        """获取管理员 Dashboard 数据.

        包含用户统计、今日登录数、操作趋势、最近日志等

        Args:
            db: 数据库会话

        Returns:
            Dashboard 完整数据
        """
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        # ===== 用户统计 =====
        total_users = db.query(func.count(User.id)).scalar() or 0
        active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar() or 0
        admin_count = db.query(func.count(User.id)).filter(User.role == _ROLE_ADMIN).scalar() or 0
        analyst_count = db.query(func.count(User.id)).filter(User.role == _ROLE_ANALYST).scalar() or 0
        user_count = db.query(func.count(User.id)).filter(User.role == _ROLE_USER).scalar() or 0

        # ===== 今日登录数 =====
        today_logins = db.query(func.count(OperationLog.id)).filter(
            OperationLog.action == "login",
            OperationLog.created_at >= today_start,
        ).scalar() or 0

        # ===== 总操作数（近30天） =====
        since_30d = now - timedelta(days=_DASHBOARD_STATS_DAYS)
        total_operations = db.query(func.count(OperationLog.id)).filter(
            OperationLog.created_at >= since_30d,
        ).scalar() or 0

        # ===== 最近7天操作趋势 =====
        daily_activity = []
        for i in range(_ACTIVITY_DAYS - 1, -1, -1):
            day_start = (now - timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            count = db.query(func.count(OperationLog.id)).filter(
                OperationLog.created_at >= day_start,
                OperationLog.created_at < day_end,
            ).scalar() or 0
            daily_activity.append({
                "date": day_start.strftime("%m-%d"),
                "count": count,
            })

        # ===== 角色分布 =====
        role_distribution = {
            "管理员": admin_count,
            "分析师": analyst_count,
            "普通用户": user_count,
        }

        # ===== 最近操作日志 =====
        recent_logs_query = (
            db.query(OperationLog, User.name)
            .join(User, OperationLog.user_id == User.id)
            .order_by(desc(OperationLog.created_at))
            .limit(_DASHBOARD_LOG_LIMIT)
            .all()
        )

        recent_logs = []
        for log, user_name in recent_logs_query:
            recent_logs.append({
                "user_name": user_name or "未知用户",
                "action": log.action,
                "details": log.details,
                "created_at": log.created_at.isoformat() if log.created_at else "",
                "status": log.status or "success",
            })

        return {
            "user_stats": {
                "total_users": total_users,
                "active_users": active_users,
                "admin_count": admin_count,
                "analyst_count": analyst_count,
                "user_count": user_count,
            },
            "today_logins": today_logins,
            "total_operations": total_operations,
            "daily_activity": daily_activity,
            "role_distribution": role_distribution,
            "recent_logs": recent_logs,
        }


# 全局服务实例
admin_service = AdminService()
