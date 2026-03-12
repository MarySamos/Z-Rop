"""预测相关的 Pydantic 模型.

定义客户预测的数据格式
"""
from pydantic import BaseModel, Field


class CustomerData(BaseModel):
    """客户数据模型"""
    age: int = Field(35, description="年龄")
    job: str = Field("management", description="职业")
    marital: str = Field("married", description="婚姻状况")
    education: str = Field("secondary", description="教育程度")
    default_credit: str = Field("no", description="是否有违约记录")
    balance: int = Field(1000, description="账户余额")
    housing: str = Field("yes", description="是否有住房贷款")
    loan: str = Field("no", description="是否有个人贷款")
    contact: str = Field("cellular", description="联系方式")
    day: int = Field(15, description="最后一次联系日期")
    month: str = Field("may", description="最后一次联系月份")
    duration: int = Field(300, description="最后一次通话时长（秒）")
    campaign: int = Field(2, description="本次营销活动的联系次数")
    pdays: int = Field(-1, description="距离上次营销联系的天数")
    previous: int = Field(0, description="之前营销活动的联系次数")
    poutcome: str = Field("unknown", description="之前营销活动的结果")


class PredictionResponse(BaseModel):
    """预测结果"""
    prediction: int = Field(..., description="预测结果（0/1）")
    probability: float = Field(..., description="预测概率")
    label: str = Field(..., description="预测标签")
    confidence: str = Field(..., description="置信度")


class FeatureImportance(BaseModel):
    """特征重要性"""
    feature: str = Field(..., description="特征名称")
    importance: float = Field(..., description="重要性得分")
