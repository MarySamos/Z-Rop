"""追问分析 LLM Agent"""
from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.core.config import settings


class FollowupAgent:
    """追问分析 LLM Agent"""

    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.LLM_MODEL,
            temperature=0.3,
            openai_api_key=settings.ZHIPU_API_KEY,
            openai_api_base=settings.LLM_API_BASE
        )
        self.parser = StrOutputParser()
        self._build_chain()

    def _build_chain(self):
        """构建追问分析链"""
        self.explain_prompt = ChatPromptTemplate.from_messages([
            ("system", """你是数据分析专家。请分析用户对查询结果的追问。

## 你的任务
用户问"为什么"或"什么意思"，你需要：
1. 分析数据特点
2. 给出合理的业务解释
3. 保持专业但易懂

## 分析角度
- 数据分布（集中/分散）
- 数值大小（高/低/平均）
- 比例关系（占比、转化率）
- 业务含义（可能的原因）

注意：如果数据不足以得出结论，诚实说明。"""),
            ("user", """## 上一次查询
{last_query}

## 数据结果
{data_preview}

## 用户追问
{message}

请分析：""")
        ])

        self.explain_chain = self.explain_prompt | self.llm | self.parser

    async def explain(
        self,
        message: str,
        last_query: str,
        data_preview: str
    ) -> str:
        """解释型追问"""
        return await self.explain_chain.ainvoke({
            "message": message,
            "last_query": last_query,
            "data_preview": data_preview
        })
