"""数据分析相关的 Pydantic 模型.

定义聚类分析和统计分析的数据格式
"""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ClusteringRequest(BaseModel):
    """聚类分析请求"""
    n_clusters: Optional[int] = Field(None, description="聚类数量（None 则自动选择）")
    features: Optional[List[str]] = Field(None, description="特征列表")
    max_k: int = Field(10, description="最大聚类数")


class ClusterProfile(BaseModel):
    """聚类画像"""
    cluster_id: int = Field(..., description="聚类 ID")
    size: int = Field(..., description="样本数量")
    percentage: float = Field(..., description="占比")
    label: str = Field(..., description="聚类标签")
    conversion_rate: Optional[float] = Field(None, description="转化率")
    dominant_job: Optional[str] = Field(None, description="主要职业")
    dominant_marital: Optional[str] = Field(None, description="主要婚姻状况")


class StatisticsResponse(BaseModel):
    """统计分析响应"""
    row_count: int = Field(..., description="总行数")
    column_count: int = Field(..., description="列数")
    numeric_stats: Dict[str, Any] = Field(default_factory=dict, description="数值列统计")
    categorical_stats: Dict[str, Any] = Field(default_factory=dict, description="分类列统计")
