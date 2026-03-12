"""ML 预测服务.

加载训练好的模型，提供预测功能
"""
import json
import pickle
from pathlib import Path
from typing import Dict, List

import pandas as pd

# Model file names
_MODEL_FILENAME = "conversion_model.pkl"
_METADATA_FILENAME = "conversion_model_metadata.json"
_ENCODERS_FILENAME = "label_encoders.pkl"

# Prediction thresholds
_CONFIDENCE_HIGH_THRESHOLD = 0.7
_CONFIDENCE_LOW_THRESHOLD = 0.3

# Default values
_TOP_N_DEFAULT = 10


class MLService:
    """机器学习预测服务"""

    def __init__(self):
        self.model = None
        self.label_encoders: Dict = {}
        self.metadata: Dict = {}
        self.feature_names: List[str] = []
        self._load_model()

    def _load_model(self) -> None:
        """加载模型和相关文件"""
        models_dir = Path(__file__).parent.parent.parent.parent / "data" / "models"

        try:
            model_path = models_dir / _MODEL_FILENAME
            if model_path.exists():
                with open(model_path, "rb") as f:
                    self.model = pickle.load(f)
                print(f"[OK] Model loaded successfully: {model_path}")
            else:
                print(f"[WARNING] Model file not found: {model_path}")
                return

            metadata_path = models_dir / _METADATA_FILENAME
            if metadata_path.exists():
                with open(metadata_path, "r", encoding="utf-8") as f:
                    self.metadata = json.load(f)
                self.feature_names = self.metadata.get("feature_names", [])

            encoders_path = models_dir / _ENCODERS_FILENAME
            if encoders_path.exists():
                with open(encoders_path, "rb") as f:
                    self.label_encoders = pickle.load(f)

        except Exception as e:
            print(f"[ERROR] Model loading failed: {e}")

    def predict(self, customer_data: dict) -> dict:
        """预测单个客户的转化概率.

        Args:
            customer_data: 客户特征字典

        Returns:
            预测结果，包含概率和标签
        """
        if self.model is None:
            return {"error": "模型未加载"}

        try:
            df = pd.DataFrame([customer_data])

            for col, encoder in self.label_encoders.items():
                if col in df.columns:
                    df[col] = df[col].apply(
                        lambda x: encoder.transform([x])[0]
                        if x in encoder.classes_
                        else 0
                    )

            df = df.reindex(columns=self.feature_names, fill_value=0)

            probability = self.model.predict_proba(df)[0][1]
            prediction = self.model.predict(df)[0]

            confidence = self._get_confidence_level(probability)

            return {
                "prediction": int(prediction),
                "probability": round(float(probability) * 100, 2),
                "label": "会订阅" if prediction == 1 else "不会订阅",
                "confidence": confidence,
            }

        except Exception as e:
            return {"error": str(e)}

    def _get_confidence_level(self, probability: float) -> str:
        """根据概率返回置信度等级"""
        if probability > _CONFIDENCE_HIGH_THRESHOLD or probability < _CONFIDENCE_LOW_THRESHOLD:
            return "高"
        return "中"

    def batch_predict(self, customers: List[Dict]) -> List[Dict]:
        """批量预测"""
        return [self.predict(c) for c in customers]

    def get_feature_importance(self, top_n: int = _TOP_N_DEFAULT) -> List[Dict]:
        """获取特征重要性排名"""
        if self.model is None:
            return []

        importances = self.model.feature_importances_
        feature_imp = sorted(
            zip(self.feature_names, importances),
            key=lambda x: x[1],
            reverse=True,
        )[:top_n]

        return [
            {"feature": f, "importance": round(float(i), 4)}
            for f, i in feature_imp
        ]

    def get_model_info(self) -> dict:
        """获取模型信息"""
        return {
            "model_loaded": self.model is not None,
            "model_type": self.metadata.get("model_type", "Unknown"),
            "training_date": self.metadata.get("training_date", "Unknown"),
            "n_features": len(self.feature_names),
            "feature_names": self.feature_names,
        }


# 全局服务实例
ml_service = MLService()
