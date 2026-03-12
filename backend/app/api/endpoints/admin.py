"""管理员 API 接口.

包括：用户管理、系统概览驾驶舱
所有接口需要管理员权限
"""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import require_admin
from app.core.database import get_db
from app.db.models import User
from app.schemas.admin import (
    AdminDashboardResponse,
    AdminUserCreate,
    UserListResponse,
    UserRoleUpdate,
    UserStatusUpdate,
)
from app.services.admin_service import admin_service
from app.services.log_service import log_service

logger = logging.getLogger(__name__)

router = APIRouter()

# 分页默认值
_PAGE_DEFAULT = 1
_PAGE_MIN = 1
_PAGE_SIZE_DEFAULT = 20
_PAGE_SIZE_MIN = 5
_PAGE_SIZE_MAX = 100


@router.get("/users", response_model=UserListResponse)
async def get_users(
    page: int = Query(default=_PAGE_DEFAULT, ge=_PAGE_MIN, description="页码"),
    page_size: int = Query(default=_PAGE_SIZE_DEFAULT, ge=_PAGE_SIZE_MIN, le=_PAGE_SIZE_MAX, description="每页数量"),
    role: Optional[str] = Query(default=None, description="按角色筛选"),
    keyword: Optional[str] = Query(default=None, description="搜索姓名或工号"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """获取用户列表（管理员专用）.

    支持分页、角色筛选、关键词搜索
    """
    try:
        result = admin_service.get_all_users(
            db, page=page, page_size=page_size, role=role, keyword=keyword
        )
        return result
    except Exception as e:
        logger.error("获取用户列表失败: %s", str(e))
        raise HTTPException(status_code=500, detail="获取用户列表失败")


@router.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: AdminUserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """管理员创建用户.

    可指定任意角色（user/admin/analyst）
    """
    try:
        result = admin_service.create_user_by_admin(
            db,
            employee_id=user_data.employee_id,
            name=user_data.name,
            password=user_data.password,
            department=user_data.department,
            role=user_data.role,
        )

        # 记录操作日志
        log_service.log_action(
            db=db,
            user_id=current_user.id,
            action="admin_create_user",
            resource="user",
            details=f"管理员创建用户: {user_data.name} ({user_data.employee_id}), 角色: {user_data.role}",
            status="success",
        )

        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("创建用户失败: %s", str(e))
        raise HTTPException(status_code=500, detail="创建用户失败")


@router.put("/users/{user_id}/role")
async def update_user_role(
    user_id: int,
    role_data: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """修改用户角色（管理员专用）.

    不允许管理员修改自己的角色
    """
    # 防止管理员修改自己的角色
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能修改自己的角色")

    try:
        result = admin_service.update_user_role(db, user_id=user_id, new_role=role_data.role)

        # 记录操作日志
        log_service.log_action(
            db=db,
            user_id=current_user.id,
            action="admin_change_role",
            resource="user",
            details=f"修改用户ID={user_id}的角色: {result['old_role']} → {result['new_role']}",
            status="success",
        )

        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("修改角色失败: %s", str(e))
        raise HTTPException(status_code=500, detail="修改角色失败")


@router.put("/users/{user_id}/status")
async def update_user_status(
    user_id: int,
    status_data: UserStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """启用/禁用用户（管理员专用）.

    不允许管理员禁用自己
    """
    # 防止管理员禁用自己
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能禁用自己的账号")

    try:
        result = admin_service.update_user_status(
            db, user_id=user_id, is_active=status_data.is_active
        )

        # 记录操作日志
        action_text = "启用" if status_data.is_active else "禁用"
        log_service.log_action(
            db=db,
            user_id=current_user.id,
            action="admin_change_status",
            resource="user",
            details=f"{action_text}用户ID={user_id}",
            status="success",
        )

        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("修改用户状态失败: %s", str(e))
        raise HTTPException(status_code=500, detail="修改用户状态失败")


@router.get("/dashboard", response_model=AdminDashboardResponse)
async def get_admin_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """获取管理员 Dashboard 数据.

    包含用户统计、今日登录数、操作趋势、角色分布、最近日志
    """
    try:
        result = admin_service.get_admin_dashboard(db)
        return result
    except Exception as e:
        logger.error("获取管理员 Dashboard 失败: %s", str(e))
        raise HTTPException(status_code=500, detail="获取管理员概览数据失败")
