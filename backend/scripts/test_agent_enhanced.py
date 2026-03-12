"""
智能体增强功能测试脚本

测试三项核心优化：
1. Few-Shot Prompt 优化
2. SQL 自愈机制
3. 对话上下文增强
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.graphs.nodes import (
    intent_parser,
    text_to_sql,
    execute_query,
    resolve_user_input,
    generate_answer,
)
from app.graphs.state import create_initial_state
from app.graphs.enums import Intent


# 装饰器：模拟 AgentState
def mock_state(**kwargs):
    """创建模拟的状态对象"""
    default_state = {
        "user_input": "",
        "resolved_input": None,
        "chat_history": [],
        "messages": [],
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
    default_state.update(kwargs)
    return default_state


def print_separator(title: str):
    """打印分隔符"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


# ========== 测试 1: 意图识别（Few-Shot 优化）==========
def test_intent_classification():
    """测试意图识别功能"""
    print_separator("测试 1: 意图识别（Few-Shot 优化）")

    test_cases = [
        "查询30岁以下的客户",
        "统计各职业的客户数量",
        "画出年龄分布图",
        "什么是KYC认证",
        "你好",
        "按教育程度统计转化率",  # 混合意图
    ]

    for query in test_cases:
        state = mock_state(user_input=query)
        result = intent_parser(state)

        intent = result.get("intent", "unknown")
        print(f"❓ 问题: {query}")
        print(f"   识别意图: {intent}")
        print()


# ========== 测试 2: Text-to-SQL（Few-Shot 优化）==========
def test_text_to_sql():
    """测试 SQL 生成功能"""
    print_separator("测试 2: Text-to-SQL（Few-Shot 优化）")

    test_cases = [
        "查询30岁以下的客户",
        "统计各职业的客户数量",
        "按教育程度统计转化率",
        "查询通话时长超过5分钟的客户",
    ]

    for query in test_cases:
        state = mock_state(user_input=query, resolved_input=query)
        result = text_to_sql(state)

        sql = result.get("generated_sql", "")
        print(f"❓ 问题: {query}")
        print(f"生成的 SQL:")
        print(f"   {sql[:100]}...")
        print()


# ========== 测试 3: 指代消解（上下文增强）==========
def test_coreference_resolution():
    """测试指代消解功能"""
    print_separator("测试 3: 指代消解（上下文增强）")

    # 模拟对话历史
    chat_history = [
        {"user": "查询30岁以下的客户", "assistant": "查询到 8234 条记录..."},
    ]

    test_cases = [
        ("它们有多少", chat_history),  # 有指代
        ("查询已婚客户", chat_history),  # 无指代
    ]

    for query, history in test_cases:
        state = mock_state(user_input=query, chat_history=history)
        result = resolve_user_input(state)

        resolved = result.get("resolved_input", query)
        print(f"原始问题: {query}")
        print(f"消解后:   {resolved}")
        print(f"是否消解: {'✅ 是' if resolved != query else '❌ 否'}")
        print()


# ========== 测试 4: SQL 自愈机制 ==========
def test_sql_self_healing():
    """测试 SQL 自愈机制"""
    print_separator("测试 4: SQL 自愈机制")

    # 测试错误的 SQL
    bad_sql = "SELECT * FROM marketing_data WHERE agee < 30"  # agee 拼写错误
    state = mock_state(generated_sql=bad_sql)

    print(f"原始 SQL: {bad_sql}")
    print("(这会触发自愈机制)")
    print()

    # 注意：实际的自愈机制在 execute_query 节点中
    # 这里只是演示，完整测试需要连接数据库


# ========== 测试 5: 对话上下文增强 ==========
def test_context_aware_generation():
    """测试上下文感知的回答生成"""
    print_separator("测试 5: 对话上下文增强")

    chat_history = [
        {"user": "查询30岁以下的客户", "assistant": "查询到 8234 条 30 岁以下的客户记录"},
    ]

    test_cases = [
        ("分析一下这些客户", chat_history, "有追问"),
        ("查询已婚客户", chat_history, "新问题"),
    ]

    for query, history, case_type in test_cases:
        state = mock_state(
            user_input=query,
            chat_history=history,
            sql_result=[{"age": 25, "job": "student"}] * 10,
            intent="query",
        )
        result = generate_answer(state)

        answer = result.get("final_answer", "")
        print(f"问题: {query}")
        print(f"类型: {case_type}")
        print(f"回答: {answer[:100]}...")
        print()


# ========== 主函数 ==========
def main():
    """运行所有测试"""
    print("\n")
    print("🤖 BankAgent 智能体增强功能测试")
    print("=" * 60)

    tests = [
        ("意图识别（Few-Shot）", test_intent_classification),
        ("Text-to-SQL（Few-Shot）", test_text_to_sql),
        ("指代消解", test_coreference_resolution),
        ("SQL 自愈机制", test_sql_self_healing),
        ("上下文感知", test_context_aware_generation),
    ]

    print("\n可用测试:")
    for i, (name, _) in enumerate(tests, 1):
        print(f"  {i}. {name}")
    print(f"  0. 全部测试")

    choice = input("\n请选择测试编号 (0-5): ").strip()

    if choice == "0":
        for name, test_func in tests:
            try:
                test_func()
            except Exception as e:
                print(f"❌ 测试失败: {e}")
    elif choice.isdigit() and 1 <= int(choice) <= len(tests):
        idx = int(choice) - 1
        name, test_func = tests[idx]
        try:
            test_func()
        except Exception as e:
            print(f"❌ 测试失败: {e}")
    else:
        print("无效的选择")

    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
