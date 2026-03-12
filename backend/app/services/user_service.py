"""用户认证服务.

处理用户注册、登录、JWT 生成和验证
"""
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import User

# User role constants
_ROLE_USER = "user"
_ROLE_ADMIN = "admin"
_ROLE_ANALYST = "analyst"

# Default user values
_DEFAULT_DEPARTMENT = None
_DEFAULT_ROLE = _ROLE_USER


# ========== Password Functions ==========

def hash_password(password: str) -> str:
    """密码哈希函数（SHA-256）.

    Note: 演示用途，生产环境建议使用 bcrypt
    """
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return hash_password(plain_password) == hashed_password


# ========== JWT Functions ==========

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建 JWT 访问令牌.

    Args:
        data: 要编码的数据（通常是 user_id 或 employee_id）
        expires_delta: 过期时间增量

    Returns:
        JWT token 字符串
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_token(token: str) -> Optional[str]:
    """验证 JWT 令牌并返回用户 ID.

    Args:
        token: JWT token 字符串

    Returns:
        用户工号（employee_id）如果验证成功，否则返回 None
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        employee_id: str = payload.get("sub")
        return employee_id if employee_id else None
    except JWTError:
        return None


# ========== User Functions ==========

def authenticate_user(db: Session, employee_id: str, password: str) -> Optional[User]:
    """验证用户凭据.

    Args:
        db: 数据库会话
        employee_id: 用户工号
        password: 密码

    Returns:
        User 对象如果验证成功，否则返回 None
    """
    user = db.query(User).filter(User.employee_id == employee_id).first()

    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    if not user.is_active:
        return None

    return user


def create_user(
    db: Session,
    employee_id: str,
    name: str,
    password: str,
    department: Optional[str] = _DEFAULT_DEPARTMENT,
    role: str = _DEFAULT_ROLE,
) -> User:
    """创建新用户.

    Args:
        db: 数据库会话
        employee_id: 工号
        name: 姓名
        password: 密码（明文）
        department: 部门
        role: 角色（user/admin/analyst）

    Returns:
        创建的 User 对象
    """
    hashed_pwd = hash_password(password)

    db_user = User(
        employee_id=employee_id,
        name=name,
        department=department,
        hashed_password=hashed_pwd,
        role=role,
        is_active=True
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def get_user_by_employee_id(db: Session, employee_id: str) -> Optional[User]:
    """根据工号获取用户"""
    return db.query(User).filter(User.employee_id == employee_id).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """根据 ID 获取用户"""
    return db.query(User).filter(User.id == user_id).first()
