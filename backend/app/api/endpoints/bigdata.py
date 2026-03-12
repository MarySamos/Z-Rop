"""大数据实验室 API 端点.

提供 Spark 相关功能接口
"""
import logging

from fastapi import APIRouter, HTTPException

from app.services.spark_service import spark_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/benchmark")
async def run_benchmark():
    """执行大数据基准测试：Pandas vs Spark 性能对比.

    使用真实的银行营销数据进行分析对比，包括：
    - 客户群体分析
    - 营销转化漏斗分析
    - 客户价值排名
    - 复杂营销效果分析
    - 客户行为模式分析

    Returns:
        各项测试的耗时对比结果，包括数据加载时间
    """
    try:
        logger.info("开始执行真实数据的基准测试")
        return spark_service.run_benchmark()

    except Exception as e:
        logger.error(f"基准测试失败: {e}")
        detail = _get_spark_error_detail(str(e))
        raise HTTPException(status_code=500, detail=detail)


def _get_spark_error_detail(error_msg: str) -> str:
    """将 Spark 错误转换为友好的错误提示"""
    error_patterns = [
        ("Java", "Spark 启动失败：未检测到 Java 环境。请确保已安装 JDK 8/11/17/21。"),
        ("JAVA_HOME", "Spark 启动失败：未检测到 Java 环境。请确保已安装 JDK 8/11/17/21。"),
        ("pyspark", "PySpark 模块未安装。请运行: pip install pyspark findspark"),
        ("findspark", "PySpark 模块未安装。请运行: pip install pyspark findspark"),
        ("postgresql", "数据库连接失败：请确保 PostgreSQL 正在运行，且已下载 JDBC 驱动到 libs/ 目录"),
        ("jdbc", "数据库连接失败：请确保 PostgreSQL 正在运行，且已下载 JDBC 驱动到 libs/ 目录"),
        ("relation", "数据表不存在：请确保已导入银行营销数据到 marketing_data 表"),
        ("table", "数据表不存在：请确保已导入银行营销数据到 marketing_data 表"),
    ]

    for pattern, message in error_patterns:
        if pattern in error_msg.lower():
            return message

    return f"执行失败: {error_msg}"


@router.get("/status")
async def spark_status():
    """检查 Spark 环境状态"""
    try:
        spark = spark_service.get_spark()
        return {
            "status": "running",
            "app_name": spark.sparkContext.appName,
            "master": spark.sparkContext.master,
            "version": spark.version,
            "cores": spark.sparkContext.defaultParallelism,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
        }
