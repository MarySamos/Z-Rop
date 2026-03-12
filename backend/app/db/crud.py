"""CRUD Operations Module.

提供基础数据库操作
"""
from collections.abc import Generator
from typing import List, Optional

from sqlalchemy import select, desc
from sqlalchemy.orm import Session

from app.db.models import OperationLog, User

# Query defaults
_DEFAULT_SKIP = 0
_DEFAULT_LIMIT = 100
_DEFAULT_STATUS = "success"


# ========== User CRUD Operations ==========

def get_user(db: Session, user_id: int) -> Optional[User]:
    """根据 ID 获取用户"""
    return db.get(User, user_id)


def get_user_by_employee_id(db: Session, employee_id: str) -> Optional[User]:
    """根据工号获取用户"""
    stmt = select(User).where(User.employee_id == employee_id)
    return db.execute(stmt).scalar_one_or_none()


def get_users(
    db: Session,
    skip: int = _DEFAULT_SKIP,
    limit: int = _DEFAULT_LIMIT,
    active_only: bool = False,
) -> List[User]:
    """获取用户列表（可选过滤活跃用户）"""
    stmt = select(User)
    if active_only:
        stmt = stmt.where(User.is_active == True)
    stmt = stmt.offset(skip).limit(limit)
    return list(db.execute(stmt).scalars().all())


def create_user(db: Session, user_data: dict) -> User:
    """创建新用户"""
    db_user = User(**user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user_data: dict) -> Optional[User]:
    """更新用户信息"""
    db_user = get_user(db, user_id)
    if not db_user:
        return None

    for key, value in user_data.items():
        if hasattr(db_user, key):
            setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    """软删除用户（设置 is_active 为 False）"""
    db_user = get_user(db, user_id)
    if db_user:
        db_user.is_active = False
        db.commit()
        return True
    return False


# ========== OperationLog CRUD Operations ==========

def create_log(
    db: Session,
    user_id: int,
    action: str,
    resource: Optional[str] = None,
    details: Optional[str] = None,
    ip_address: Optional[str] = None,
    status: str = _DEFAULT_STATUS,
) -> OperationLog:
    """创建操作日志记录"""
    db_log = OperationLog(
        user_id=user_id,
        action=action,
        resource=resource,
        details=details,
        ip_address=ip_address,
        status=status,
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


def get_logs(
    db: Session,
    skip: int = _DEFAULT_SKIP,
    limit: int = _DEFAULT_LIMIT,
    user_id: Optional[int] = None,
    action: Optional[str] = None,
) -> List[OperationLog]:
    """获取操作日志列表（可选过滤）"""
    stmt = select(OperationLog)
    if user_id:
        stmt = stmt.where(OperationLog.user_id == user_id)
    if action:
        stmt = stmt.where(OperationLog.action == action)
    stmt = stmt.order_by(desc(OperationLog.created_at)).offset(skip).limit(limit)
    return list(db.execute(stmt).scalars().all())
