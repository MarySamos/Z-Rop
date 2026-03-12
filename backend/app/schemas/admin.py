"""管理员相关的 Pydantic 模型.

定义管理员接口的请求和响应数据格式
"""
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


# ========== 请求模型 ==========

class UserRoleUpdate(BaseModel):
    """修改用户角色的请求模型"""
    role: str = Field(..., description="新角色 (user/admin/analyst)")

    @field_validator('role')
    @classmethod
    def validate_role(cls, v: str) -> str:
        """验证角色是否合法"""
        allowed_roles = {"user", "admin", "analyst"}
        if v not in allowed_roles:
            raise ValueError(f"角色必须是以下之一: {', '.join(allowed_roles)}")
        return v


class UserStatusUpdate(BaseModel):
    """修改用户状态的请求模型"""
    is_active: bool = Field(..., description="是否激活")


class AdminUserCreate(BaseModel):
    """管理员创建用户的请求模型"""
    employee_id: str = Field(..., description="工号")
    name: str = Field(..., description="姓名")
    password: str = Field(..., min_length=6, description="密码（至少6位）")
    department: Optional[str] = Field(None, description="部门")
    role: str = Field("user", description="角色 (user/admin/analyst)")

    @field_validator('role')
    @classmethod
    def validate_role(cls, v: str) -> str:
        """验证角色是否合法"""
        allowed_roles = {"user", "admin", "analyst"}
        if v not in allowed_roles:
            raise ValueError(f"角色必须是以下之一: {', '.join(allowed_roles)}")
        return v


# ========== 响应模型 ==========

class UserItem(BaseModel):
    """用户列表中的单个用户信息"""
    id: int
    employee_id: str
    name: str
    department: Optional[str] = None
    role: str
    is_active: bool
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """用户列表响应模型"""
    users: List[UserItem]
    total: int
    page: int
    page_size: int


class UserStats(BaseModel):
    """用户统计数据"""
    total_users: int = Field(description="总用户数")
    active_users: int = Field(description="活跃用户数")
    admin_count: int = Field(description="管理员数量")
    analyst_count: int = Field(description="分析师数量")
    user_count: int = Field(description="普通用户数量")


class DailyActivity(BaseModel):
    """每日活动数据"""
    date: str
    count: int


class RecentLog(BaseModel):
    """最近操作日志"""
    user_name: str
    action: str
    details: Optional[str] = None
    created_at: str
    status: str


class AdminDashboardResponse(BaseModel):
    """管理员 Dashboard 响应模型"""
    user_stats: UserStats
    today_logins: int = Field(description="今日登录数")
    total_operations: int = Field(description="总操作数（近30天）")
    daily_activity: List[DailyActivity] = Field(description="最近7天操作趋势")
    role_distribution: dict = Field(description="角色分布")
    recent_logs: List[RecentLog] = Field(description="最近操作日志")
