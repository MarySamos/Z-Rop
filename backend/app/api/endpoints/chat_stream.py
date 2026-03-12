"""Chat API with Streaming Support（增强版）.

支持流式输出的智能对话端点

增强功能：
- 查询重写
- 查询类型检测
- 更丰富的流式事件
"""
import json
import traceback
import asyncio
from collections.abc import AsyncGenerator
from typing import Dict, Any, List

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.graphs.state import create_initial_state
from app.graphs.workflow import agent_app
from app.graphs.query_rewrite import rewrite_query, detect_query_type, expand_query
from app.schemas.chat import ChatStreamRequest, ChatResponse

router = APIRouter()

# SSE headers
_SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no",
}

# Default values
_DEFAULT_SESSION_SUFFIX = "_default"
_DEFAULT_USER_ID = "default"


# ========== 流式事件类 ==========
class StreamEvent:
    """流式事件构建器"""

    @staticmethod
    def intent(intent: str, confidence: float = 0.0) -> str:
        """意图识别事件"""
        return f"data: {json.dumps({'type': 'intent', 'intent': intent, 'confidence': confidence}, ensure_ascii=False)}\n\n"

    @staticmethod
    def thinking(message: str = "", step: str = "") -> str:
        """思考状态事件"""
        return f"data: {json.dumps({'type': 'thinking', 'message': message, 'step': step}, ensure_ascii=False)}\n\n"

    @staticmethod
    def rewritten(original: str, rewritten: str, reason: str) -> str:
        """查询重写事件"""
        return f"data: {json.dumps({'type': 'rewritten', 'original': original, 'rewritten': rewritten, 'reason': reason}, ensure_ascii=False)}\n\n"

    @staticmethod
    def sql(sql: str, corrected: bool = False) -> str:
        """SQL 事件"""
        return f"data: {json.dumps({'type': 'sql', 'sql': sql, 'corrected': corrected}, ensure_ascii=False)}\n\n"

    @staticmethod
    def query_result(row_count: int, preview: List[Dict] = None) -> str:
        """查询结果事件"""
        return f"data: {json.dumps({'type': 'query_result', 'row_count': row_count, 'preview': preview or []}, ensure_ascii=False)}\n\n"

    @staticmethod
    def text(content: str) -> str:
        """文本内容事件"""
        return f"data: {json.dumps({'type': 'text', 'content': content}, ensure_ascii=False)}\n\n"

    @staticmethod
    def answer(content: str) -> str:
        """最终回答事件"""
        return f"data: {json.dumps({'type': 'answer', 'content': content}, ensure_ascii=False)}\n\n"

    @staticmethod
    def error(message: str) -> str:
        """错误事件"""
        return f"data: {json.dumps({'type': 'error', 'message': message}, ensure_ascii=False)}\n\n"

    @staticmethod
    def done() -> str:
        """完成事件"""
        return f"data: {json.dumps({'type': 'done'}, ensure_ascii=False)}\n\n"


# ========== 增强的流式响应生成器 ==========
async def stream_chat_response_enhanced(
    message: str,
    session_id: str,
    user_id: str = _DEFAULT_USER_ID,
    chat_history: List[Dict] = None,
) -> AsyncGenerator[str, None]:
    """增强的流式生成聊天响应.

    增强功能：
    - 查询重写
    - 查询类型检测
    - 更丰富的流式事件

    Args:
        message: 用户消息
        session_id: 会话ID
        user_id: 用户ID
        chat_history: 对话历史

    Yields:
        Server-Sent Events 格式的数据
    """
    try:
        # 1. 查询类型检测
        query_info = detect_query_type(message)
        yield StreamEvent.thinking("正在分析查询...", "detect")

        # 2. 查询重写
        rewrite_result = rewrite_query(message, chat_history)

        if rewrite_result["changed"]:
            yield StreamEvent.rewritten(
                original=message,
                rewritten=rewrite_result["rewritten"],
                reason=rewrite_result["reason"]
            )
            message = rewrite_result["rewritten"]

        # 3. 发送查询信息
        yield json.dumps({
            "type": "query_info",
            "info": query_info
        }, ensure_ascii=False) + "\n\n"

        # 4. 思考状态
        yield StreamEvent.thinking("正在识别意图...", "intent")

        # 5. 配置
        config = {
            "configurable": {
                "thread_id": session_id,
                "user_id": user_id,
            }
        }

        initial_state = create_initial_state(
            user_input=message,
            chat_history=chat_history or []
        )

        # 6. 执行工作流
        current_intent = None
        current_sql = None

        async for event in agent_app.astream(
            initial_state,
            config=config,
            stream_mode="updates",
        ):
            for node_name, node_output in event.items():
                # 意图识别节点
                if node_name == "intent_parser":
                    current_intent = node_output.get("intent", "")
                    yield StreamEvent.intent(current_intent)
                    yield StreamEvent.thinking("正在生成查询...", "sql_gen")

                # 指代消解节点
                elif node_name == "resolve_input":
                    resolved = node_output.get("resolved_input")
                    if resolved and resolved != message:
                        yield StreamEvent.thinking(f"已解析指代：{resolved}", "resolve")

                # SQL 生成节点
                elif node_name == "text_to_sql":
                    current_sql = node_output.get("generated_sql", "")
                    corrected = node_output.get("sql_corrected", False)
                    yield StreamEvent.sql(current_sql, corrected)
                    yield StreamEvent.thinking("正在执行查询...", "execute")

                # 查询执行节点
                elif node_name == "execute_query":
                    if node_output.get("sql_error"):
                        yield StreamEvent.error(node_output["sql_error"])
                    else:
                        data = node_output.get("sql_result", [])
                        preview = data[:5] if data else []
                        yield StreamEvent.query_result(len(data), preview)
                        yield StreamEvent.thinking("正在生成回答...", "generate")

                # 统计分析节点
                elif node_name == "data_analysis":
                    stats = node_output.get("stats_result", {})
                    yield json.dumps({
                        "type": "stats",
                        "stats": stats
                    }, ensure_ascii=False) + "\n\n"
                    yield StreamEvent.thinking("正在生成回答...", "generate")

                # 可视化节点
                elif node_name == "visualization":
                    chart_html = node_output.get("chart_html", "")
                    chart_type = node_output.get("chart_type", "")
                    yield json.dumps({
                        "type": "visualization",
                        "chart": chart_html,
                        "chart_type": chart_type
                    }, ensure_ascii=False) + "\n\n"

                # 最终回答节点
                elif node_name == "generate_answer":
                    answer = node_output.get("final_answer", "")
                    # 流式输出回答（模拟打字效果）
                    for char in answer:
                        yield StreamEvent.text(char)
                        await asyncio.sleep(0.01)  # 打字效果

                # 错误处理
                elif "error_message" in node_output:
                    yield StreamEvent.error(node_output["error_message"])

        yield StreamEvent.done()

    except Exception as e:
        traceback.print_exc()
        yield StreamEvent.error(f"处理请求时出错: {str(e)}")
        yield StreamEvent.done()


# ========== API 端点 ==========
@router.post("/stream")
async def chat_stream(request: ChatStreamRequest):
    """流式聊天端点（增强版）.

    使用 Server-Sent Events (SSE) 实现实时流式输出

    请求示例：
    ```json
    {
        "message": "查询余额大于5000的客户",
        "session_id": "user123_session456",
        "user_id": "user123",
        "history": []
    }
    ```

    响应事件类型：
    - thinking: 正在处理（包含 step 信息）
    - rewritten: 查询重写结果
    - query_info: 查询类型信息
    - intent: 意图识别结果
    - sql: 生成的 SQL 语句
    - query_result: 查询结果（row_count + preview）
    - stats: 统计分析结果
    - visualization: 可视化图表
    - text: 文本内容（逐字符输出）
    - answer: 最终回答
    - error: 错误信息
    - done: 流结束

    Returns:
        StreamingResponse: SSE 流式响应
    """
    session_id = request.session_id or f"{request.user_id}{_DEFAULT_SESSION_SUFFIX}"

    return StreamingResponse(
        stream_chat_response_enhanced(
            message=request.message,
            session_id=session_id,
            user_id=request.user_id,
            chat_history=request.history,
        ),
        media_type="text/event-stream",
        headers=_SSE_HEADERS,
    )


@router.post("/smart")
async def chat_smart(request: ChatStreamRequest) -> ChatResponse:
    """智能聊天端点（带查询重写和类型检测）.

    这是一个非流式的端点，返回完整的响应，包含：
    - 查询重写信息
    - 查询类型检测
    - 意图识别
    - 建议的可视化类型

    适用于需要快速获取查询元信息的场景
    """
    try:
        # 查询重写
        rewrite_result = rewrite_query(request.message, request.history)

        # 查询类型检测
        query_info = detect_query_type(request.message)

        # 构建响应
        answer_parts = []

        if rewrite_result["changed"]:
            answer_parts.append(f"📝 **查询已优化**：{rewrite_result['rewritten']}")

        answer_parts.extend([
            f"🎯 **意图类型**：{query_info['type']}",
            f"📊 **复杂度**：{query_info['complexity']}",
        ])

        if query_info.get("has_aggregation"):
            answer_parts.append("📈 **包含聚合**：是")
        if query_info.get("has_grouping"):
            answer_parts.append("📋 **包含分组**：是")
        if query_info.get("suggested_visualization"):
            answer_parts.append(f"📈 **建议图表**：{query_info['suggested_visualization']}")

        return ChatResponse(
            answer="\n\n".join(answer_parts),
            chart=None,
            sql=None,
            intent=query_info["type"],
            session_id=request.session_id,
        )

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze")
async def analyze_query(request: ChatStreamRequest):
    """查询分析端点.

    返回对用户查询的详细分析，不执行实际查询
    """
    try:
        # 查询重写
        rewrite_result = rewrite_query(request.message, request.history)

        # 查询类型检测
        query_info = detect_query_type(request.message)

        # 查询扩展
        expansions = expand_query(request.message)

        return {
            "original_query": request.message,
            "rewritten_query": rewrite_result.get("rewritten"),
            "was_rewritten": rewrite_result.get("changed", False),
            "rewrite_reason": rewrite_result.get("reason"),
            "query_info": query_info,
            "expanded_queries": expansions,
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
