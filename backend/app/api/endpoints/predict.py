"""预测 API 接口.

提供客户转化预测功能
"""
from typing import List

from fastapi import APIRouter, HTTPException

from app.schemas.predict import CustomerData, FeatureImportance, PredictionResponse
from app.services.ml_service import ml_service

router = APIRouter()


@router.post("/single", response_model=PredictionResponse)
async def predict_single(customer: CustomerData):
    """单个客户转化预测.

    输入客户信息，返回订阅定期存款的概率
    """
    result = ml_service.predict(customer.model_dump())

    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    return result


@router.post("/batch")
async def predict_batch(customers: List[CustomerData]):
    """批量客户预测"""
    data = [c.model_dump() for c in customers]
    results = ml_service.batch_predict(data)
    return {"predictions": results}


@router.get("/importance", response_model=List[FeatureImportance])
async def get_feature_importance():
    """获取特征重要性排名.

    哪些因素最影响客户转化
    """
    return ml_service.get_feature_importance()


@router.get("/info")
async def get_model_info():
    """获取模型信息"""
    return ml_service.get_model_info()
