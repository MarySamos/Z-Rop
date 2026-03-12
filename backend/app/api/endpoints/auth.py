"""用户认证相关接口.

包括：注册、登录、获取当前用户信息
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.db.models import User
from app.schemas.user import Token, UserCreate, UserLogin, UserResponse
from app.services.user_service import (
    authenticate_user,
    create_access_token,
    create_user,
    get_user_by_employee_id,
)

router = APIRouter(prefix="/auth", tags=["认证"])

# Default role
_DEFAULT_ROLE = "user"


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """用户注册接口.

    Args:
        user_data: 用户注册信息（工号、姓名、密码、部门）
        db: 数据库会话

    Returns:
        Token 响应（包含 access_token 和用户信息）

    Raises:
        HTTPException 400: 用户已存在或数据验证失败
        HTTPException 500: 数据库错误
    """
    try:
        existing_user = get_user_by_employee_id(db, employee_id=user_data.employee_id)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该工号已被注册",
            )

        new_user = create_user(
            db=db,
            employee_id=user_data.employee_id,
            name=user_data.name,
            password=user_data.password,
            department=user_data.department,
            role=user_data.role or _DEFAULT_ROLE,
        )

        access_token = create_access_token(data={"sub": new_user.employee_id})

        return Token(
            access_token=access_token,
            user=UserResponse.model_validate(new_user),
        )

    except HTTPException:
        raise
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="注册失败，请稍后重试",
        )


@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """用户登录接口.

    Args:
        user_data: 用户登录信息（工号、密码）
        db: 数据库会话

    Returns:
        Token 响应（包含 access_token 和用户信息）

    Raises:
        HTTPException 401: 工号或密码错误
        HTTPException 500: 服务器错误
    """
    user = authenticate_user(
        db=db,
        employee_id=user_data.employee_id,
        password=user_data.password,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="工号或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.employee_id})

    from app.services.log_service import log_service

    log_service.log_action(
        db=db,
        user_id=user.id,
        action="login",
        resource="auth",
        details=f"用户 {user.name} 登录成功",
        status="success",
    )

    return Token(
        access_token=access_token,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前登录用户信息.

    Args:
        current_user: 当前登录用户（从 JWT token 解析）

    Returns:
        用户信息
    """
    return UserResponse.model_validate(current_user)
