"""
测试 Checkpoint 和流式输出功能
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.graphs.workflow import agent_app
from app.graphs.state import create_initial_state
from app.graphs.checkpoint_manager import get_checkpointer


def test_checkpoint():
    """测试 Checkpoint 功能"""
    print("=" * 60)
    print("[TEST] Testing Checkpoint Functionality")
    print("=" * 60)

    # 检查 checkpointer 是否正常初始化
    checkpointer = get_checkpointer()
    print(f"[OK] Checkpointer type: {type(checkpointer).__name__}")

    # 测试会话 ID
    session_id = "test_session_001"

    # 第一轮对话
    print("\n[INFO] Round 1 conversation...")
    config1 = {
        "configurable": {
            "thread_id": session_id,
            "user_id": "test_user"
        }
    }

    initial_state1 = create_initial_state(
        user_input="你好",
        chat_history=[]
    )

    try:
        final_state1 = agent_app.invoke(initial_state1, config=config1)
        print(f"[OK] Round 1 succeeded")
        print(f"   Intent: {final_state1.get('intent')}")
        print(f"   Answer: {final_state1.get('final_answer', '')[:50]}...")
    except Exception as e:
        print(f"[ERROR] Round 1 failed: {e}")
        return False

    # 第二轮对话（测试会话记忆）
    print("\n[INFO] Round 2 conversation (testing session memory)...")
    config2 = {
        "configurable": {
            "thread_id": session_id,  # 使用相同的 session_id
            "user_id": "test_user"
        }
    }

    initial_state2 = create_initial_state(
        user_input="查询余额大于5000的客户",
        chat_history=[]
    )

    try:
        final_state2 = agent_app.invoke(initial_state2, config=config2)
        print(f"[OK] Round 2 succeeded")
        print(f"   Intent: {final_state2.get('intent')}")
        print(f"   SQL: {final_state2.get('generated_sql', '')[:50]}...")
    except Exception as e:
        print(f"[ERROR] Round 2 failed: {e}")
        return False

    print("\n[OK] Checkpoint functionality test passed!")
    return True


def test_streaming():
    """测试流式输出功能"""
    print("\n" + "=" * 60)
    print("[TEST] Testing Streaming Functionality")
    print("=" * 60)

    import asyncio

    async def stream_test():
        session_id = "test_session_002"

        config = {
            "configurable": {
                "thread_id": session_id,
                "user_id": "test_user"
            }
        }

        initial_state = create_initial_state(
            user_input="你好，请介绍一下你自己",
            chat_history=[]
        )

        print("\n[INFO] Starting stream output...\n")

        event_count = 0
        async for event in agent_app.astream(
            initial_state,
            config=config,
            stream_mode="updates"
        ):
            for node_name, node_output in event.items():
                event_count += 1
                print(f"[NODE {event_count}] {node_name}")

                # 显示关键信息
                if node_name == "intent_parser":
                    intent = node_output.get("intent", "")
                    print(f"   Intent: {intent}")

                elif node_name == "generate_answer":
                    answer = node_output.get("final_answer", "")
                    print(f"   Answer: {answer[:50]}...")

        print(f"\n[OK] Stream output completed, {event_count} nodes executed")
        return True

    try:
        result = asyncio.run(stream_test())
        return result
    except Exception as e:
        print(f"[ERROR] Streaming test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("\n[START] Testing Checkpoint and Streaming Features\n")

    # 测试 Checkpoint
    checkpoint_ok = test_checkpoint()

    # 测试流式输出
    streaming_ok = test_streaming()

    # 总结
    print("\n" + "=" * 60)
    print("[SUMMARY] Test Results")
    print("=" * 60)
    print(f"Checkpoint: {'[PASS]' if checkpoint_ok else '[FAIL]'}")
    print(f"Streaming: {'[PASS]' if streaming_ok else '[FAIL]'}")

    if checkpoint_ok and streaming_ok:
        print("\n[SUCCESS] All tests passed!")
        return 0
    else:
        print("\n[WARNING] Some tests failed, please check configuration")
        return 1


if __name__ == "__main__":
    exit(main())
