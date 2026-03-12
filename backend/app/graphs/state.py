"""LangGraph 智能体状态定义（完整增强版）.

定义 Agent 工作流中的状态结构和数据流

新增字段：
- original_input: 原始用户输入
- resolved_input: 指代消解后的用户输入
- rewrite_reason: 查询重写原因
- sql_corrected: SQL 是否被自动修正
"""
from collections.abc import KeysView
from typing import Any, Dict, List, Optional

from langgraph.graph import MessagesState

from app.graphs.enums import Intent


# ========== Agent 状态定义 ==========
class AgentState(MessagesState):
    """BankAgent 工作流状态（完整增强版）.

    继承自 MessagesState，支持消息历史管理

    新增功能：
    - 查询重写支持
    - 指代消解支持
    - SQL 修正标记
    - 增强的上下文管理
    """
    # 用户输入
    user_input: str                    # 当前用户输入（可能已被重写）
    original_input: Optional[str] = None  # 原始用户输入（重写前）

    # 指代消解后的输入
    resolved_input: Optional[str] = None

    # 查询重写信息
    rewrite_reason: Optional[str] = None

    # 聊天历史
    chat_history: List[Dict[str, str]]

    # 意图识别结果
    intent: Optional[Intent] = None

    # Text-to-SQL 相关
    generated_sql: Optional[str] = None
    sql_result: Optional[List[Dict[str, Any]]] = None
    sql_error: Optional[str] = None
    sql_corrected: bool = False  # 标记SQL是否被自动修正

    # 统计分析相关
    stats_result: Optional[Dict[str, Any]] = None

    # 可视化相关
    chart_html: Optional[str] = None
    chart_type: Optional[str] = None

    # 最终答案
    final_answer: Optional[str] = None

    # RAG 知识问答相关
    rag_context: Optional[str] = None
    rag_sources: Optional[List[Dict[str, Any]]] = None

    # 错误信息
    error_message: Optional[str] = None


# ========== 状态创建函数 ==========
def create_initial_state(
    user_input: str,
    chat_history: Optional[List[Dict[str, str]]] = None,
) -> Dict[str, Any]:
    """创建初始状态.

    Args:
        user_input: 用户输入的问题
        chat_history: 聊天历史记录

    Returns:
        初始化的状态字典
    """
    return {
        "user_input": user_input,
        "original_input": None,  # 由 query_rewrite 节点填充
        "resolved_input": None,  # 由 resolve_input 节点填充
        "rewrite_reason": None,
        "chat_history": chat_history or [],
        "messages": [],  # LangGraph MessagesState 要求的字段
        "intent": None,
        "generated_sql": None,
        "sql_result": None,
        "sql_error": None,
        "sql_corrected": False,
        "stats_result": None,
        "chart_html": None,
        "chart_type": None,
        "final_answer": None,
        "rag_context": None,
        "rag_sources": None,
        "error_message": None,
    }


# ========== 辅助函数：格式化聊天历史 ==========
def format_chat_history_for_prompt(chat_history: List[Dict[str, str]], max_turns: int = 3) -> str:
    """格式化聊天历史用于 Prompt.

    Args:
        chat_history: 聊天历史
        max_turns: 最大轮数

    Returns:
        格式化的历史字符串
    """
    if not chat_history:
        return "（无对话历史）"

    recent = chat_history[-max_turns:] if len(chat_history) > max_turns else chat_history

    lines = []
    for i, turn in enumerate(recent, 1):
        if isinstance(turn, dict):
            user_msg = turn.get("user", turn.get("question", ""))
            assistant_msg = turn.get("assistant", turn.get("answer", ""))
            lines.append(f"Q{i}: {user_msg}")
            lines.append(f"A{i}: {assistant_msg[:150]}...")
        else:
            lines.append(f"第{i}轮: {str(turn)[:200]}")

    return "\n".join(lines)
