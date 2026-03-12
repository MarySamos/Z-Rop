"""查询重写模块.

优化用户的模糊查询，使其更准确
"""
import logging
from typing import Dict, Any, List, Optional

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.core.config import settings
from app.graphs.prompts import MARKETING_DATA_SCHEMA

logger = logging.getLogger(__name__)


# 全局 LLM 实例
_rewrite_llm = ChatOpenAI(
    model=settings.LLM_MODEL,
    temperature=0.1,
    openai_api_key=settings.ZHIPU_API_KEY,
    openai_api_base=settings.LLM_API_BASE
)


# ========== 常见查询模式映射 ==========
QUERY_PATTERNS = {
    # 年龄相关
    r"年轻人": "age < 35",
    r"中年人": "age >= 35 AND age < 55",
    r"老年人": "age >= 55",
    r"小孩": "age < 18",

    # 余额相关
    r"高余额": "balance > 5000",
    r"低余额": "balance < 1000",
    r"负余额": "balance < 0",

    # 职业相关
    r"学生": "job = 'student'",
    r"退休": "job = 'retired'",

    # 贷款相关
    r"有房贷": "housing = 'yes'",
    r"无房贷": "housing = 'no'",
    r"有贷款": "loan = 'yes'",
    r"无贷款": "loan = 'no'",
}


# ========== 常见同义词映射 ==========
SYNONYMS = {
    "查询": ["显示", "列出", "查找", "搜索", "看看", "看看有哪些"],
    "统计": ["计算", "汇总", "分析"],
    "画图": ["可视化", "图表", "图形", "画出"],
    "客户": ["用户", "人"],
    "转化": ["订阅", "购买", "成功"],
    "已婚": ["结婚"],
    "单身": ["未婚", "离婚"],
}


def rewrite_query(
    query: str,
    chat_history: Optional[List[Dict[str, str]]] = None
) -> Dict[str, Any]:
    """
    查询重写主函数

    Args:
        query: 原始查询
        chat_history: 对话历史

    Returns:
        {
            "rewritten": "重写后的查询",
            "changed": True/False,
            "reason": "重写原因"
        }
    """
    original = query.strip()

    # 1. 检查是否需要重写
    needs_rewrite, reason = _check_rewrite_needed(original, chat_history)

    if not needs_rewrite:
        return {"rewritten": original, "changed": False, "reason": "无需重写"}

    # 2. 尝试规则-based 重写
    rule_result = _rule_based_rewrite(original)
    if rule_result != original:
        logger.info(f"📝 规则重写: '{original}' -> '{rule_result}'")
        return {
            "rewritten": rule_result,
            "changed": True,
            "reason": "规则匹配"
        }

    # 3. LLM 重写（针对复杂场景）
    llm_result = _llm_based_rewrite(original, chat_history)
    if llm_result != original:
        logger.info(f"🤖 LLM 重写: '{original}' -> '{llm_result}'")
        return {
            "rewritten": llm_result,
            "changed": True,
            "reason": "LLM 增强"
        }

    return {"rewritten": original, "changed": False, "reason": "重写未生效"}


def _check_rewrite_needed(
    query: str,
    chat_history: Optional[List[Dict[str, str]]]
) -> tuple:
    """检查是否需要重写"""
    # 条件1：查询太短
    if len(query) < 5:
        return True, "查询过短"

    # 条件2：包含口语化表达
    colloquial_words = ["那个", "这个", "啥", "哪些", "多少个"]
    if any(word in query for word in colloquial_words):
        return True, "口语化表达"

    # 条件3：指代词
    pronouns = ["它", "它们", "那些", "这个", "这些"]
    if any(word in query for word in pronouns):
        return True, "包含指代词"

    # 条件4：有对话历史但查询不完整
    if chat_history and len(query) < 10:
        return True, "上下文相关"

    return False, ""


def _rule_based_rewrite(query: str) -> str:
    """基于规则的查询重写"""
    result = query

    # 替换同义词
    for standard, synonyms in SYNONYMS.items():
        for syn in synonyms:
            if syn in result:
                result = result.replace(syn, standard)

    # 扩展缩写
    abbreviations = {
        "KYC": "KYC认证",
        "ATM": "ATM机",
        "APP": "手机APP",
    }
    for abbr, full in abbreviations.items():
        if abbr.upper() in result.upper():
            result = result.replace(abbr, full)

    # 补充缺失的宾语
    if result in ["查询", "显示", "列出", "统计"]:
        result = f"{result}所有客户信息"

    return result


def _llm_based_rewrite(
    query: str,
    chat_history: Optional[List[Dict[str, str]]]
) -> str:
    """基于 LLM 的查询重写"""
    # 构建上下文
    context = ""
    if chat_history:
        last_turn = chat_history[-1]
        if isinstance(last_turn, dict):
            last_q = last_turn.get("user", last_turn.get("question", ""))
            context = f"\n上一轮问题：{last_q}"

    prompt = ChatPromptTemplate.from_messages([
        ("system", """你是一个查询重写助手。请将用户的简短或不完整的查询重写为完整、清晰的查询。

数据库结构（用于参考）：
{schema}

重写规则：
1. 保持查询意图不变
2. 补充缺失的宾语和条件
3. 使用清晰、完整的表述
4. 不要改变原意
5. 如果原查询已经很完整，保持不变

只返回重写后的查询，不要解释。"""),
        ("user", "原查询：{query}{context}\n\n重写后的查询：")
    ])

    try:
        chain = prompt | _rewrite_llm | StrOutputParser()
        rewritten = chain.invoke({
            "query": query,
            "context": context,
            "schema": _get_schema_summary()
        }).strip()
        return rewritten
    except Exception as e:
        logger.warning(f"LLM 重写失败: {e}")
        return query


def _get_schema_summary() -> str:
    """获取简化的 Schema 摘要"""
    return """
核心字段：
- age: 年龄
- job: 职业（admin, technician, student, retired等）
- marital: 婚姻状况（married, single, divorced）
- education: 教育程度
- balance: 账户余额
- housing: 是否有住房贷款
- loan: 是否有个人贷款
- month: 联系月份
- duration: 通话时长（秒）
- y: 是否转化（yes/no）
"""


# ========== 查询扩展（用于增强检索）==========
def expand_query(query: str) -> List[str]:
    """
    查询扩展 - 生成相关查询用于增强检索

    Args:
        query: 原始查询

    Returns:
        扩展查询列表
    """
    expansions = [query]

    # 1. 同义词扩展
    for standard, synonyms in SYNONYMS.items():
        for syn in synonyms:
            if syn in query:
                for other_syn in synonyms:
                    if other_syn != syn:
                        expansions.append(query.replace(syn, other_syn))

    # 2. 相关维度扩展
    if "职业" in query or "job" in query.lower():
        expansions.append("按教育程度统计")
        expansions.append("按婚姻状况统计")

    if "年龄" in query or "age" in query.lower():
        expansions.append("按余额统计")
        expansions.append("按通话时长统计")

    # 去重并限制数量
    return list(dict.fromkeys(expansions))[:5]


# ========== 查询类型检测 ==========
def detect_query_type(query: str) -> Dict[str, Any]:
    """
    检测查询类型和复杂度

    Returns:
        {
            "type": "query/stats/viz/rag/chat",
            "complexity": "simple/medium/complex",
            "has_aggregation": True/False,
            "has_grouping": True/False,
            "suggested_visualization": "bar/line/pie/..."
        }
    """
    query_lower = query.lower()

    # 检测意图类型
    intent_type = "chat"
    if any(kw in query for kw in ["查询", "显示", "列出", "有多少"]):
        intent_type = "query"
    elif any(kw in query for kw in ["统计", "平均", "总计", "分布", "占比"]):
        intent_type = "stats"
    elif any(kw in query for kw in ["画图", "图表", "柱状图", "饼图", "折线图"]):
        intent_type = "viz"
    elif any(kw in query for kw in ["什么是", "如何", "为什么", "解释"]):
        intent_type = "rag"

    # 检测复杂度
    complexity = "simple"
    has_aggregation = False
    has_grouping = False

    # 检测聚合关键词
    agg_keywords = ["统计", "平均", "总计", "求和", "计数", "最大", "最小"]
    if any(kw in query for kw in agg_keywords):
        has_aggregation = True
        complexity = "medium"

    # 检测分组关键词
    group_keywords = ["按", "分组", "每个", "各个"]
    if any(kw in query for kw in group_keywords):
        has_grouping = True
        complexity = "medium"

    # 多条件查询
    condition_count = query.count("和") + query.count("且") + query.count("或")
    if condition_count >= 2:
        complexity = "complex"

    # 建议的可视化类型
    suggested_viz = None
    if intent_type in ["query", "stats"]:
        if "趋势" in query or "月份" in query or "时间" in query:
            suggested_viz = "line"
        elif "占比" in query or "分布" in query:
            suggested_viz = "pie"
        else:
            suggested_viz = "bar"

    return {
        "type": intent_type,
        "complexity": complexity,
        "has_aggregation": has_aggregation,
        "has_grouping": has_grouping,
        "suggested_visualization": suggested_viz
    }
