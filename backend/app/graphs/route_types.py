"""路由相关数据结构"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from app.graphs.enums import RouteType, FollowupType


@dataclass
class RouteDecision:
    """路由决策结果"""
    route_type: RouteType
    confidence: float
    reasoning: str = ""

    # 提取的实体（用于查询）
    extracted_entities: Dict[str, Any] = field(default_factory=dict)

    # 追问相关
    followup_type: Optional[FollowupType] = None
    drilldown_dimension: Optional[str] = None  # 下钻维度

    def is_query_type(self) -> bool:
        """是否是查询类型（包括修正）"""
        return self.route_type in (RouteType.QUERY, RouteType.CORRECTION)

    def is_followup(self) -> bool:
        """是否是追问"""
        return self.route_type == RouteType.FOLLOWUP


@dataclass
class FollowupAction:
    """追问动作"""
    type: str  # EXPLAIN, DETAIL, DRILLDOWN, COMPARE, TREND, NEW_QUERY
    data: Optional[List[Dict]] = None
    context: Optional[str] = None
    dimension: Optional[str] = None  # 下钻维度
    reason: str = ""
    last_query: Optional[str] = None  # 上一次查询
    last_sql: Optional[str] = None   # 上一次 SQL
