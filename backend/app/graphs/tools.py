"""LangGraph 智能体工具集.

定义 Agent 可调用的各种工具函数
"""
from typing import Any, Dict, List, Optional

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import engine

# ========== 表名白名单（防止 SQL 注入）==========
ALLOWED_TABLES = {
    "marketing_data",
    "users",
    "knowledge_docs",
    "conversations",
    "messages",
}

# Query defaults
_MAX_ROWS_DEFAULT = 100
_TABLE_SAMPLE_LIMIT = 5
_DISTRIBUTION_LIMIT = 20


def validate_table_name(table_name: str) -> None:
    """验证表名是否在白名单中.

    Args:
        table_name: 表名

    Raises:
        ValueError: 如果表名不在白名单中
    """
    if table_name not in ALLOWED_TABLES:
        raise ValueError(f"不允许访问表: {table_name}")


# ========== 数据库工具 ==========

def execute_sql(sql: str, max_rows: int = _MAX_ROWS_DEFAULT) -> Dict[str, Any]:
    """执行 SQL 查询并返回结果.

    Args:
        sql: 要执行的 SQL 语句
        max_rows: 最大返回行数

    Returns:
        {
            "success": bool,
            "data": List[dict],  # 查询结果
            "row_count": int,
            "columns": List[str],
            "error": Optional[str]
        }
    """
    sql_upper = sql.strip().upper()
    if not sql_upper.startswith("SELECT"):
        return {
            "success": False,
            "data": [],
            "row_count": 0,
            "columns": [],
            "error": "安全限制：只允许执行 SELECT 查询语句",
        }

    dangerous_keywords = ["DROP", "DELETE", "TRUNCATE", "UPDATE", "INSERT", "ALTER", "CREATE", "GRANT"]
    for keyword in dangerous_keywords:
        if keyword in sql_upper:
            return {
                "success": False,
                "data": [],
                "row_count": 0,
                "columns": [],
                "error": f"安全限制：禁止使用 {keyword} 操作",
            }

    try:
        with engine.connect() as conn:
            result = conn.execute(text(sql))
            columns = list(result.keys())
            rows = result.fetchmany(max_rows)

            data = [dict(zip(columns, row)) for row in rows]
            row_count = len(data)

        return {
            "success": True,
            "data": data,
            "row_count": row_count,
            "columns": columns,
            "error": None,
        }

    except SQLAlchemyError as e:
        return {
            "success": False,
            "data": [],
            "row_count": 0,
            "columns": [],
            "error": f"SQL 执行错误: {str(e)}",
        }
    except Exception as e:
        return {
            "success": False,
            "data": [],
            "row_count": 0,
            "columns": [],
            "error": f"未知错误: {str(e)}",
        }


def get_table_schema(table_name: str = "marketing_data") -> str:
    """获取表的 Schema 信息.

    Args:
        table_name: 表名

    Returns:
        Schema 描述字符串
    """
    try:
        validate_table_name(table_name)

        with engine.connect() as conn:
            result = conn.execute(text(f"""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position
            """))

            columns = result.fetchall()

            if not columns:
                return f"表 {table_name} 不存在或没有列"

            schema_info = f"表名: {table_name}\n\n列信息:\n"
            schema_info += "-" * 50 + "\n"

            for col_name, data_type, nullable in columns:
                null_str = "NULL" if nullable == "YES" else "NOT NULL"
                schema_info += f"  {col_name:<20} {data_type:<15} {null_str}\n"

            count_result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            row_count = count_result.fetchone()[0]
            schema_info += f"\n总行数: {row_count:,}"

        return schema_info

    except Exception as e:
        return f"获取 Schema 失败: {str(e)}"


def get_table_sample(table_name: str = "marketing_data", limit: int = _TABLE_SAMPLE_LIMIT) -> List[Dict]:
    """获取表的样本数据.

    Args:
        table_name: 表名
        limit: 样本行数

    Returns:
        样本数据列表
    """
    validate_table_name(table_name)

    result = execute_sql(f"SELECT * FROM {table_name} LIMIT {limit}")
    return result.get("data", [])


# ========== 统计分析工具 ==========

def get_basic_stats(table_name: str = "marketing_data") -> Dict[str, Any]:
    """获取表的基础统计信息.

    Returns:
        {
            "row_count": int,
            "numeric_stats": {...},
            "categorical_stats": {...}
        }
    """
    try:
        validate_table_name(table_name)

        import pandas as pd

        df = pd.read_sql(f"SELECT * FROM {table_name}", engine)

        stats = {
            "row_count": len(df),
            "column_count": len(df.columns),
            "numeric_stats": {},
            "categorical_stats": {},
        }

        numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns
        for col in numeric_cols:
            if col != "id":
                stats["numeric_stats"][col] = {
                    "mean": round(df[col].mean(), 2),
                    "median": round(df[col].median(), 2),
                    "std": round(df[col].std(), 2),
                    "min": int(df[col].min()),
                    "max": int(df[col].max()),
                }

        categorical_cols = df.select_dtypes(include=["object"]).columns
        for col in categorical_cols:
            value_counts = df[col].value_counts().head(10).to_dict()
            stats["categorical_stats"][col] = {
                "unique_count": df[col].nunique(),
                "top_values": value_counts,
            }

        return stats

    except Exception as e:
        return {"error": str(e)}


def get_column_distribution(
    column_name: str,
    table_name: str = "marketing_data",
) -> Dict[str, Any]:
    """获取单列的分布信息.

    Args:
        column_name: 列名
        table_name: 表名

    Returns:
        分布统计结果
    """
    validate_table_name(table_name)

    sql = f"""
        SELECT {column_name}, COUNT(*) as count
        FROM {table_name}
        GROUP BY {column_name}
        ORDER BY count DESC
        LIMIT {_DISTRIBUTION_LIMIT}
    """

    result = execute_sql(sql)

    if result["success"]:
        return {
            "column": column_name,
            "distribution": result["data"],
            "total_categories": len(result["data"]),
        }
    return {"error": result["error"]}


def get_conversion_rate(
    group_by_column: str = None,
    table_name: str = "marketing_data",
    target_column: str = "y",
) -> Dict[str, Any]:
    """计算转化率（按指定维度分组）.

    Args:
        group_by_column: 分组列（可选，为 None 时返回整体转换率）
        table_name: 表名
        target_column: 目标变量列 (y)

    Returns:
        各组的转化率
    """
    validate_table_name(table_name)

    # 如果没有指定分组列，返回整体转换率
    if not group_by_column or group_by_column.lower() == "none":
        sql = f"""
            SELECT
                'overall' as category,
                COUNT(*) as total,
                SUM(CASE WHEN {target_column} = 'yes' THEN 1 ELSE 0 END) as converted,
                ROUND(100.0 * SUM(CASE WHEN {target_column} = 'yes' THEN 1 ELSE 0 END) / COUNT(*), 2) as conversion_rate
            FROM {table_name}
        """
    else:
        sql = f"""
            SELECT
                {group_by_column},
                COUNT(*) as total,
                SUM(CASE WHEN {target_column} = 'yes' THEN 1 ELSE 0 END) as converted,
                ROUND(100.0 * SUM(CASE WHEN {target_column} = 'yes' THEN 1 ELSE 0 END) / COUNT(*), 2) as conversion_rate
            FROM {table_name}
            GROUP BY {group_by_column}
            ORDER BY conversion_rate DESC
        """

    result = execute_sql(sql)

    if result["success"]:
        return {
            "group_by": group_by_column or "overall",
            "data": result["data"],
        }
    return {"error": result["error"]}


# ========== 可视化工具 ==========

def generate_chart(
    chart_type: str,
    data: List[Dict],
    x_field: str,
    y_field: str,
    title: str = "",
) -> str:
    """生成 Pyecharts 图表 HTML.

    Args:
        chart_type: 图表类型 (bar, line, pie)
        data: 数据列表
        x_field: X 轴字段
        y_field: Y 轴字段
        title: 图表标题

    Returns:
        图表 HTML 代码
    """
    try:
        from pyecharts import options as opts
        from pyecharts.charts import Bar, Line, Pie

        x_data = [str(item.get(x_field, "")) for item in data]
        y_data = [item.get(y_field, 0) for item in data]

        if chart_type == "bar":
            chart = (
                Bar()
                .add_xaxis(x_data)
                .add_yaxis("", y_data)
                .set_global_opts(
                    title_opts=opts.TitleOpts(title=title),
                    xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45)),
                )
            )
        elif chart_type == "line":
            chart = (
                Line()
                .add_xaxis(x_data)
                .add_yaxis("", y_data, is_smooth=True)
                .set_global_opts(title_opts=opts.TitleOpts(title=title))
            )
        elif chart_type == "pie":
            pie_data = [(str(item.get(x_field, "")), item.get(y_field, 0)) for item in data]
            chart = (
                Pie()
                .add("", pie_data)
                .set_global_opts(title_opts=opts.TitleOpts(title=title))
                .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c} ({d}%)"))
            )
        else:
            return f"不支持的图表类型: {chart_type}"

        return chart.render_embed()

    except ImportError:
        return "错误: 需要安装 pyecharts 库"
    except Exception as e:
        return f"生成图表失败: {str(e)}"


# ========== 工具注册（供 LLM 调用） ==========

AVAILABLE_TOOLS = {
    "execute_sql": {
        "function": execute_sql,
        "description": "执行 SQL 查询语句，返回查询结果。只支持 SELECT 语句。",
        "parameters": {
            "sql": "要执行的 SQL 语句",
            "max_rows": "最大返回行数，默认 100",
        },
    },
    "get_basic_stats": {
        "function": get_basic_stats,
        "description": "获取表的基础统计信息，包括数值列的均值、中位数、标准差等，以及分类列的分布。",
        "parameters": {
            "table_name": "表名，默认 marketing_data",
        },
    },
    "get_column_distribution": {
        "function": get_column_distribution,
        "description": "获取指定列的值分布情况。",
        "parameters": {
            "column_name": "列名",
            "table_name": "表名，默认 marketing_data",
        },
    },
    "get_conversion_rate": {
        "function": get_conversion_rate,
        "description": "计算不同维度的转化率（y=yes 的比例）。",
        "parameters": {
            "group_by_column": "分组列",
            "table_name": "表名，默认 marketing_data",
        },
    },
    "generate_chart": {
        "function": generate_chart,
        "description": "生成可视化图表，支持 bar(柱状图)、line(折线图)、pie(饼图)。",
        "parameters": {
            "chart_type": "图表类型: bar, line, pie",
            "data": "数据列表",
            "x_field": "X 轴字段名",
            "y_field": "Y 轴字段名",
            "title": "图表标题",
        },
    },
}
"""i love codex """