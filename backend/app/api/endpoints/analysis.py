"""数据分析 API 接口.

提供聚类分析、统计分析等功能
"""
import io
import traceback

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse

from app.schemas.analysis import ClusteringRequest
from app.services.analysis_service import analysis_service

router = APIRouter()

# Query defaults
_N_CLUSTERS_DEFAULT = 4
_N_CLUSTERS_MIN = 2
_N_CLUSTERS_MAX = 10

_PCA_COMPONENTS_DEFAULT = 2
_PCA_COMPONENTS_MIN = 2
_PCA_COMPONENTS_MAX = 5

_ASSOCIATION_SUPPORT_DEFAULT = 0.1
_ASSOCIATION_SUPPORT_MIN = 0.01
_ASSOCIATION_SUPPORT_MAX = 1.0

_ASSOCIATION_CONFIDENCE_DEFAULT = 0.5
_ASSOCIATION_CONFIDENCE_MIN = 0.1
_ASSOCIATION_CONFIDENCE_MAX = 1.0

_ASSOCIATION_RULES_DEFAULT = 20
_ASSOCIATION_RULES_MIN = 5
_ASSOCIATION_RULES_MAX = 100

_CORRELATION_METHOD_DEFAULT = "pearson"
_CORRELATION_METHODS = "^(pearson|spearman|kendall)$"

_CLUSTERING_FOR_REPORT = 4


# ========== 聚类分析接口 ==========

@router.post("/clustering")
async def run_clustering(request: ClusteringRequest):
    """执行 K-Means 聚类分析.

    将客户分成不同群体，生成客户画像
    """
    try:
        return analysis_service.clustering_analysis(
            n_clusters=request.n_clusters,
            features=request.features,
            max_k=request.max_k,
        )
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="聚类分析失败")


@router.get("/clustering/quick")
async def quick_clustering(n_clusters: int = Query(default=_N_CLUSTERS_DEFAULT, ge=_N_CLUSTERS_MIN, le=_N_CLUSTERS_MAX)):
    """快速聚类分析（使用默认特征）"""
    try:
        return analysis_service.clustering_analysis(n_clusters=n_clusters)
    except Exception:
        raise HTTPException(status_code=500, detail="聚类分析失败")


# ========== 统计分析接口 ==========

@router.get("/statistics")
async def get_descriptive_statistics():
    """描述性统计分析.

    返回所有数值列的均值、中位数、标准差、分位数、偏度、峰度
    """
    try:
        return analysis_service.descriptive_statistics()
    except Exception:
        raise HTTPException(status_code=500, detail="统计分析失败")


@router.get("/quality")
async def get_data_quality():
    """数据质量报告.

    检测缺失值、异常值（3sigma法则）、数据完整性
    """
    try:
        return analysis_service.data_quality_report()
    except Exception:
        raise HTTPException(status_code=500, detail="数据质量分析失败")


@router.get("/correlation")
async def get_correlation(method: str = Query(default=_CORRELATION_METHOD_DEFAULT, pattern=_CORRELATION_METHODS)):
    """相关性分析.

    计算变量间的相关系数矩阵，返回热力图数据
    """
    try:
        return analysis_service.correlation_analysis(method=method)
    except Exception:
        raise HTTPException(status_code=500, detail="相关性分析失败")


@router.get("/distribution/{column}")
async def get_distribution(column: str):
    """单变量分布分析.

    数值型返回直方图，分类型返回值计数
    """
    try:
        result = analysis_service.distribution_analysis(column)
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="分布分析失败")


# ========== 关联规则挖掘 ==========

@router.get("/association")
async def get_association_rules(
    min_support: float = Query(default=_ASSOCIATION_SUPPORT_DEFAULT, ge=_ASSOCIATION_SUPPORT_MIN, le=_ASSOCIATION_SUPPORT_MAX),
    min_confidence: float = Query(default=_ASSOCIATION_CONFIDENCE_DEFAULT, ge=_ASSOCIATION_CONFIDENCE_MIN, le=_ASSOCIATION_CONFIDENCE_MAX),
    max_rules: int = Query(default=_ASSOCIATION_RULES_DEFAULT, ge=_ASSOCIATION_RULES_MIN, le=_ASSOCIATION_RULES_MAX),
):
    """关联规则挖掘 (Apriori算法).

    发现特征之间的关联模式，如 "高学历 + 已婚 -> 高转化"
    """
    try:
        result = analysis_service.association_rules(
            min_support=min_support,
            min_confidence=min_confidence,
            max_rules=max_rules,
        )
        if "error" in result and "需要安装" in result["error"]:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="关联规则挖掘失败")


# ========== 特征工程 ==========

@router.get("/feature-importance")
async def get_feature_importance():
    """特征重要性分析.

    使用 Random Forest 计算各特征对转化的影响程度
    """
    try:
        return analysis_service.feature_importance()
    except Exception:
        raise HTTPException(status_code=500, detail="特征重要性分析失败")


@router.get("/pca")
async def get_pca_analysis(n_components: int = Query(default=_PCA_COMPONENTS_DEFAULT, ge=_PCA_COMPONENTS_MIN, le=_PCA_COMPONENTS_MAX)):
    """PCA 降维分析.

    将高维数据降至 2D/3D 便于可视化
    """
    try:
        return analysis_service.pca_analysis(n_components=n_components)
    except Exception:
        raise HTTPException(status_code=500, detail="PCA 分析失败")


# ========== 时间序列与漏斗分析 ==========

@router.get("/time-series")
async def get_time_series():
    """时间序列趋势分析.

    按月份统计客户数、转化率，附带移动平均预测
    """
    try:
        result = analysis_service.time_series_analysis()
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="时间序列分析失败")


@router.get("/funnel")
async def get_funnel_analysis():
    """营销漏斗分析.

    各环节转化率：总客户 → 有效联系 → 深度沟通 → 多次跟进 → 最终转化
    """
    try:
        return analysis_service.funnel_analysis()
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="漏斗分析失败")


# ========== PDF 报告 ==========

@router.get("/report/pdf")
async def download_pdf_report():
    """下载数据分析 PDF 报告.

    包含数据概览、统计分析、聚类结果
    """
    from app.services.report_service import report_service

    try:
        data = {
            "quality": analysis_service.data_quality_report(),
            "statistics": analysis_service.descriptive_statistics(),
            "clustering": analysis_service.clustering_analysis(n_clusters=_CLUSTERING_FOR_REPORT),
        }

        pdf_bytes = report_service.generate_analysis_report(data)

        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=analysis_report.pdf"},
        )

    except ImportError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="生成 PDF 报告失败")
