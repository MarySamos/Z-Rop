"""仪表盘相关的 Pydantic 模型.

定义仪表盘数据的数据格式
"""
from typing import Any, List

from pydantic import BaseModel, Field


class KPIData(BaseModel):
    """KPI 指标数据"""
    total_customers: int = Field(..., description="总客户数")
    conversion_rate: float = Field(..., description="转化率")
    avg_balance: float = Field(..., description="平均账户余额")
    avg_campaign: float = Field(..., description="平均营销次数")


class ChartData(BaseModel):
    """图表数据"""
    labels: List[str] = Field(..., description="X 轴标签")
    values: List[Any] = Field(..., description="Y 轴值")


class DashboardResponse(BaseModel):
    """仪表盘响应数据"""
    kpi: KPIData = Field(..., description="KPI 指标")
    job_distribution: ChartData = Field(..., description="职业分布")
    age_distribution: ChartData = Field(..., description="年龄分布")
    conversion_by_job: ChartData = Field(..., description="按职业的转化率")
