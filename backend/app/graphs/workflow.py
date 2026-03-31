"""LangGraph 工作流定义（增强版）.

将 State, Nodes, Tools 串联成完整的图结构

新增功能：
- 指代消解节点
- 增强的意图识别
- SQL 自愈机制
- 上下文感知
- 查询重写节点
"""
from typing import Literal

from langgraph.graph import END, StateGraph

from app.graphs.checkpoint_manager import get_checkpointer
from app.graphs.nodes import (
    data_analysis,
    execute_query,
    generate_answer,
    intent_parser,
    knowledge_search,
    text_to_sql,
    visualization,
    resolve_user_input,
)
from app.graphs.state import AgentState
from app.graphs.query_rewrite import rewrite_query


def route_by_intent(state: AgentState) -> Literal["text_to_sql", "data_analysis", "knowledge_search", "generate_answer"]:
    """根据意图路由到不同节点.

    Args:
        state: 当前状态

    Returns:
        下一个节点名称
    """
    intent = state.get("intent", "chat")

    if intent == "query":
        return "text_to_sql"
    if intent == "stats":
        return "data_analysis"
    if intent == "viz":
        return "text_to_sql"  # 可视化也需要先查数据
    if intent == "rag":
        return "knowledge_search"
    return "generate_answer"


def route_after_query(state: AgentState) -> Literal["visualization", "generate_answer"]:
    """SQL执行后根据意图决定是否可视化.

    Args:
        state: 当前状态

    Returns:
        下一个节点名称
    """
    if state.get("intent") == "viz":
        return "visualization"
    return "generate_answer"


def query_rewrite_node(state: AgentState) -> dict:
    """查询重写节点.

    在意图识别之前优化用户的查询输入

    Returns:
        更新后的状态
    """
    user_input = state.get("user_input", "")
    chat_history = state.get("chat_history", [])

    rewrite_result = rewrite_query(user_input, chat_history)

    if rewrite_result["changed"]:
        logger_msg = f"📝 查询重写: '{user_input}' -> '{rewrite_result['rewritten']}'"
        print(logger_msg)  # 打印到控制台
        return {
            "user_input": rewrite_result["rewritten"],
            "original_input": user_input,
            "rewrite_reason": rewrite_result["reason"]
        }

    return {}


def create_bank_agent_graph(use_checkpoint: bool = True):
    """创建 Z-Rop 智能体工作流图（完整增强版）.

    工作流说明：
    1. query_rewrite -> 查询重写（优化模糊查询）
    2. resolve_input -> 指代消解（处理代词）
    3. intent_parser -> 意图识别（Few-Shot）
    4. 意图识别 -> 分流到不同处理路径
    5. query/viz 意图: text_to_sql -> execute_query（带自愈） -> (visualization) -> generate_answer
    6. stats 意图: data_analysis -> generate_answer
    7. rag 意图: knowledge_search -> generate_answer
    8. chat 意图: generate_answer

    增强功能：
    - Few-Shot Prompt 优化
    - SQL 错误自愈机制
    - 对话上下文增强
    - 指代消解
    - 查询重写

    Args:
        use_checkpoint: 是否启用 checkpoint（支持会话记忆）

    Returns:
        编译后的 LangGraph 应用
    """
    workflow = StateGraph(AgentState)

    # 添加节点
    workflow.add_node("query_rewrite", query_rewrite_node)  # 新增：查询重写
    workflow.add_node("resolve_input", resolve_user_input)  # 指代消解
    workflow.add_node("intent_parser", intent_parser)
    workflow.add_node("text_to_sql", text_to_sql)
    workflow.add_node("execute_query", execute_query)
    workflow.add_node("data_analysis", data_analysis)
    workflow.add_node("visualization", visualization)
    workflow.add_node("knowledge_search", knowledge_search)
    workflow.add_node("generate_answer", generate_answer)

    # 设置入口点（首先进行查询重写）
    workflow.set_entry_point("query_rewrite")

    # 查询重写 -> 指代消解 -> 意图识别
    workflow.add_edge("query_rewrite", "resolve_input")
    workflow.add_edge("resolve_input", "intent_parser")

    # 定义边关系
    workflow.add_conditional_edges(
        "intent_parser",
        route_by_intent,
        {
            "text_to_sql": "text_to_sql",
            "data_analysis": "data_analysis",
            "knowledge_search": "knowledge_search",
            "generate_answer": "generate_answer",
        },
    )

    workflow.add_edge("text_to_sql", "execute_query")

    workflow.add_conditional_edges(
        "execute_query",
        route_after_query,
        {
            "visualization": "visualization",
            "generate_answer": "generate_answer",
        },
    )

    workflow.add_edge("data_analysis", "generate_answer")
    workflow.add_edge("visualization", "generate_answer")
    workflow.add_edge("knowledge_search", "generate_answer")
    workflow.add_edge("generate_answer", END)

    checkpointer = get_checkpointer() if use_checkpoint else None
    app = workflow.compile(checkpointer=checkpointer)
    return app


# 创建全局图实例（启用 checkpoint）
agent_app = create_bank_agent_graph(use_checkpoint=True)
