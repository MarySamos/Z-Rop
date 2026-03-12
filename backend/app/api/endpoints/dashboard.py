"""Dashboard API Endpoints.

提供仪表盘数据接口
"""
import traceback

from fastapi import APIRouter, HTTPException
from sqlalchemy import text

from app.core.database import engine
from app.schemas.dashboard import ChartData, DashboardResponse, KPIData

router = APIRouter()

# Default fallback value
_DEFAULT_VALUE = 0


@router.get("/stats", response_model=DashboardResponse)
async def get_dashboard_stats():
    """获取仪表盘统计数据"""
    try:
        with engine.connect() as conn:
            kpi = _get_kpi_data(conn)
            job_distribution = _get_job_distribution(conn)
            age_distribution = _get_age_distribution(conn)
            conversion_by_job = _get_conversion_by_job(conn)

        return DashboardResponse(
            kpi=kpi,
            job_distribution=job_distribution,
            age_distribution=age_distribution,
            conversion_by_job=conversion_by_job,
        )

    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="获取仪表盘数据失败")


def _get_kpi_data(conn) -> KPIData:
    """获取 KPI 指标数据"""
    result = conn.execute(text("SELECT COUNT(*) FROM marketing_data"))
    total_customers = result.fetchone()[0]

    result = conn.execute(text("""
        SELECT ROUND(100.0 * SUM(CASE WHEN y = 'yes' THEN 1 ELSE 0 END) / COUNT(*), 2)
        FROM marketing_data
    """))
    conversion_rate = float(result.fetchone()[0] or _DEFAULT_VALUE)

    result = conn.execute(text("SELECT ROUND(AVG(balance), 2) FROM marketing_data"))
    avg_balance = float(result.fetchone()[0] or _DEFAULT_VALUE)

    result = conn.execute(text("SELECT ROUND(AVG(campaign), 2) FROM marketing_data"))
    avg_campaign = float(result.fetchone()[0] or _DEFAULT_VALUE)

    return KPIData(
        total_customers=total_customers,
        conversion_rate=conversion_rate,
        avg_balance=avg_balance,
        avg_campaign=avg_campaign,
    )


def _get_job_distribution(conn) -> ChartData:
    """获取职业分布数据"""
    result = conn.execute(text("""
        SELECT job, COUNT(*) as count
        FROM marketing_data
        GROUP BY job
        ORDER BY count DESC
    """))
    rows = result.fetchall()
    return ChartData(
        labels=[row[0] for row in rows],
        values=[row[1] for row in rows],
    )


def _get_age_distribution(conn) -> ChartData:
    """获取年龄分布数据"""
    result = conn.execute(text("""
        SELECT
            CASE
                WHEN age < 25 THEN '18-24'
                WHEN age < 35 THEN '25-34'
                WHEN age < 45 THEN '35-44'
                WHEN age < 55 THEN '45-54'
                WHEN age < 65 THEN '55-64'
                ELSE '65+'
            END as age_group,
            COUNT(*) as count
        FROM marketing_data
        GROUP BY age_group
        ORDER BY MIN(age)
    """))
    rows = result.fetchall()
    return ChartData(
        labels=[row[0] for row in rows],
        values=[row[1] for row in rows],
    )


def _get_conversion_by_job(conn) -> ChartData:
    """获取各职业转化率数据"""
    result = conn.execute(text("""
        SELECT
            job,
            ROUND(100.0 * SUM(CASE WHEN y = 'yes' THEN 1 ELSE 0 END) / COUNT(*), 2) as rate
        FROM marketing_data
        GROUP BY job
        ORDER BY rate DESC
    """))
    rows = result.fetchall()
    return ChartData(
        labels=[row[0] for row in rows],
        values=[float(row[1]) for row in rows],
    )
