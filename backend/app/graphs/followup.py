"""追问分析器

处理用户对之前结果的追问
"""
from typing import Optional
import json

from app.graphs.memory import ConversationMemory
from app.graphs.enums import FollowupType
from app.graphs.route_types import FollowupAction
from app.graphs.agents.followup_agent import FollowupAgent


class FollowupAnalyzer:
    """追问分析器

    分析和处理用户的追问
    """

    def __init__(self):
        self.agent = FollowupAgent()

    async def analyze(
        self,
        message: str,
        memory: ConversationMemory
    ) -> FollowupAction:
        """分析追问类型并生成动作"""
        # 检查是否有历史结果
        if not memory.has_query_history():
            return FollowupAction(
                type="NEW_QUERY",
                reason="没有查询历史，按新查询处理"
            )

        # 检测追问类型
        followup_type = self._detect_followup_type(message)

        if followup_type == FollowupType.EXPLAIN:
            return FollowupAction(
                type="EXPLAIN",
                data=memory.last_result,
                context=memory.current_topic,
                last_query=memory.last_query
            )

        elif followup_type == FollowupType.DRILLDOWN:
            dimension = self._extract_dimension(message)
            return FollowupAction(
                type="DRILLDOWN",
                dimension=dimension,
                context=memory.current_topic,
                last_sql=memory.last_sql
            )

        elif followup_type == FollowupType.DETAIL:
            return FollowupAction(
                type="DETAIL",
                data=memory.last_result,
                context=memory.current_topic
            )

        # 默认按新查询处理
        return FollowupAction(
            type="NEW_QUERY",
            reason="无法识别为追问类型"
        )

    async def handle(self, action: FollowupAction, memory: ConversationMemory) -> str:
        """处理追问"""
        if action.type == "EXPLAIN":
            return await self.handle_explain(action, memory)
        elif action.type == "DETAIL":
            return self.handle_detail(action)
        elif action.type == "DRILLDOWN":
            return await self.handle_drilldown(action, memory)

        return "抱歉，我不太理解你的问题。"

    async def handle_explain(self, action: FollowupAction, memory: ConversationMemory) -> str:
        """处理解释型追问"""
        if not action.data:
            return "抱歉，没有可以分析的数据。"

        # 准备数据预览
        preview = self._prepare_data_preview(action.data)

        response = await self.agent.explain(
            message="为什么？",
            last_query=action.last_query or memory.last_query,
            data_preview=preview
        )

        memory.add_message("user", "为什么？")
        memory.add_message("assistant", response)

        return response

    def handle_detail(self, action: FollowupAction) -> str:
        """处理展开型追问"""
        if not action.data:
            return "抱歉，没有可以展开的数据。"

        # 展示更多数据
        lines = [f"以下是 **{action.context}** 的详细信息：\n"]

        # 只显示前20条
        for i, row in enumerate(action.data[:20], 1):
            lines.append(f"{i}. {row}")

        if len(action.data) > 20:
            lines.append(f"\n（还有 {len(action.data) - 20} 条数据未展示）")

        return "\n".join(lines)

    async def handle_drilldown(self, action: FollowupAction, memory: ConversationMemory) -> str:
        """处理下钻型追问"""
        if not action.dimension:
            return "请问要按哪个维度细分？（如：职业、教育程度、婚姻状况）"

        # 这里应该生成新的 SQL 并执行
        # 简化处理：返回提示信息
        return f"好的，我来按 **{action.dimension}** 细分分析 {action.context}。"

    async def generate_drilldown_sql(self, action: FollowupAction, memory: ConversationMemory) -> str:
        """生成下钻 SQL"""
        dimension = action.dimension or "job"

        # 简化：在原 SQL 基础上添加 GROUP BY
        base_sql = memory.last_sql or "SELECT * FROM marketing_data"

        # 简单处理：生成新的统计 SQL
        sql = f"""
        SELECT {dimension}, COUNT(*) as count
        FROM marketing_data
        GROUP BY {dimension}
        ORDER BY count DESC
        LIMIT 20
        """.strip()

        return sql

    def _detect_followup_type(self, message: str) -> Optional[FollowupType]:
        """检测追问类型"""
        if any(word in message for word in ["为什么", "什么意思", "解释"]):
            return FollowupType.EXPLAIN

        if any(word in message for word in ["详细", "展开", "多说", "更多"]):
            return FollowupType.DETAIL

        if any(word in message for word in ["按", "细分", "分组"]):
            return FollowupType.DRILLDOWN

        return None

    def _extract_dimension(self, message: str) -> Optional[str]:
        """提取下钻维度"""
        dimensions = {
            "职业": "job",
            "job": "job",
            "教育": "education",
            "学历": "education",
            "婚姻": "marital",
            "年龄": "age",
        }

        for key, value in dimensions.items():
            if key in message:
                return value

        return None

    def _prepare_data_preview(self, data: list) -> str:
        """准备数据预览"""
        if not data:
            return "（无数据）"

        preview = json.dumps(data[:5], ensure_ascii=False, indent=2, default=str)

        if len(data) > 5:
            preview += f"\n...（还有 {len(data) - 5} 条）"

        return preview
