"""测试追问分析器"""
import pytest
from app.graphs.followup import FollowupAnalyzer
from app.graphs.route_types import FollowupAction
from app.graphs.memory import ConversationMemory
from app.graphs.enums import FollowupType


@pytest.mark.asyncio
async def test_explain_followup():
    """测试解释型追问"""
    analyzer = FollowupAnalyzer()
    memory = ConversationMemory(session_id="s1", user_id="u1")
    memory.last_query = "查询30岁以下的客户"
    memory.last_result = [
        {"age": 25, "job": "student", "y": "no"},
        {"age": 28, "job": "student", "y": "no"},
    ]

    action = FollowupAction(
        type=FollowupType.EXPLAIN,
        data=memory.last_result,
        context=memory.current_topic
    )

    response = await analyzer.handle(action, memory)

    assert response
    assert len(response) > 10


@pytest.mark.asyncio
async def test_drilldown_followup():
    """测试下钻型追问"""
    analyzer = FollowupAnalyzer()
    memory = ConversationMemory(session_id="s1", user_id="u1")
    memory.last_query = "查询30岁以下的客户"
    memory.last_sql = "SELECT * FROM marketing_data WHERE age < 30"

    action = FollowupAction(
        type=FollowupType.DRILLDOWN,
        dimension="job",
        context="30岁以下客户"
    )

    sql = await analyzer.generate_drilldown_sql(action, memory)

    assert "job" in sql.lower()
    assert "group by" in sql.lower()


@pytest.mark.asyncio
async def test_no_history_followup():
    """测试无历史时的追问"""
    analyzer = FollowupAnalyzer()
    memory = ConversationMemory(session_id="s1", user_id="u1")
    # 没有查询历史

    action = await analyzer.analyze("为什么转化率低？", memory)

    assert action.type == "NEW_QUERY"
