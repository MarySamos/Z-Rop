"""Chat API Endpoints.

处理智能对话请求（支持会话记忆）
"""
import traceback

from fastapi import APIRouter, HTTPException

from app.graphs.state import create_initial_state
from app.graphs.workflow import agent_app
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter()

# Default session suffix and messages
_DEFAULT_SESSION_SUFFIX = "_session"
_DEFAULT_ANSWER = "抱歉，我没有生成回答。"
_DEFAULT_INTENT = "unknown"


@router.post("/send", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """发送消息给智能体（支持会话记忆）.

    工作流程：
    1. 初始化状态
    2. 运行 LangGraph 工作流（使用 checkpoint 保存会话状态）
    3. 提取并返回结果

    Checkpoint 支持：
    - 如果提供 session_id，会从之前的会话中恢复状态
    - 同一个 session_id 的对话会保持上下文记忆
    - 如果不提供 session_id，将作为新会话处理

    请求示例：
    ```json
    {
        "message": "查询余额大于5000的客户",
        "session_id": "user123_session456",
        "user_id": "user123"
    }
    ```
    """
    try:
        session_id = request.session_id or f"{request.user_id}{_DEFAULT_SESSION_SUFFIX}"

        config = {
            "configurable": {
                "thread_id": session_id,
                "user_id": request.user_id,
            }
        }

        initial_state = create_initial_state(
            user_input=request.message,
            chat_history=request.history,
        )

        final_state = agent_app.invoke(initial_state, config=config)

        return ChatResponse(
            answer=final_state.get("final_answer", _DEFAULT_ANSWER),
            chart=final_state.get("chart_html"),
            sql=final_state.get("generated_sql"),
            intent=final_state.get("intent", _DEFAULT_INTENT),
            session_id=session_id,
        )

    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="处理请求失败")


@router.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """清除指定会话的记忆.

    Args:
        session_id: 要清除的会话ID

    Returns:
        成功/失败消息
    """
    try:
        config = {"configurable": {"thread_id": session_id}}

        initial_state = create_initial_state(user_input="", chat_history=[])

        agent_app.update_state(config, initial_state)

        return {"status": "success", "message": f"会话 {session_id} 已清除"}

    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="清除会话失败")

