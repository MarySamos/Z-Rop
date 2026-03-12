"""
机器学习模型训练脚本 - 银行营销转化预测

训练一个 Random Forest 模型来预测客户是否会订阅定期存款

使用方法:
    cd backend
    python scripts/train_model.py
"""
import sys
import os
from pathlib import Path
import pickle
import json
from datetime import datetime

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
from sqlalchemy import create_engine

# Scikit-learn
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score
)

from app.core.config import settings


class ModelTrainer:
    """机器学习模型训练器"""

    def __init__(self):
        """初始化训练器"""
        self.engine = create_engine(settings.DATABASE_URL)
        self.model = None
        self.label_encoders = {}
        self.feature_names = []

    def load_data(self):
        """
        从数据库加载营销数据

        Returns:
            DataFrame: 加载的数据
        """
        print("📊 正在从数据库加载数据...")

        try:
            query = "SELECT * FROM marketing_data"
            df = pd.read_sql(query, self.engine)

            print(f"✅ 数据加载成功")
            print(f"   - 数据行数: {len(df)}")
            print(f"   - 数据列数: {len(df.columns)}")

            return df

        except Exception as e:
            print(f"❌ 错误: 数据加载失败 - {str(e)}")
            return None

    def preprocess_data(self, df: pd.DataFrame):
        """
        数据预处理

        Args:
            df: 原始数据

        Returns:
            X: 特征矩阵
            y: 目标变量
        """
        print("\n🔧 正在进行数据预处理...")

        # 删除不需要的列
        cols_to_drop = ['id', 'created_at']
        df = df.drop(columns=[col for col in cols_to_drop if col in df.columns])

        # 分离特征和目标变量
        X = df.drop('y', axis=1)
        y = df['y']

        # 目标变量编码 (yes/no -> 1/0)
        y = y.map({'yes': 1, 'no': 0})

        print(f"   - 正样本数量: {y.sum()}")
        print(f"   - 负样本数量: {len(y) - y.sum()}")
        print(f"   - 正样本比例: {y.mean():.2%}")

        # 处理分类变量
        categorical_cols = X.select_dtypes(include=['object']).columns.tolist()
        print(f"\n   分类变量: {categorical_cols}")

        for col in categorical_cols:
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col].astype(str))
            self.label_encoders[col] = le

        self.feature_names = X.columns.tolist()

        print(f"✅ 预处理完成")
        print(f"   - 特征数量: {len(self.feature_names)}")

        return X, y

    def train_model(self, X: pd.DataFrame, y: pd.Series):
        """
        训练 Random Forest 模型

        Args:
            X: 特征矩阵
            y: 目标变量

        Returns:
            训练好的模型
        """
        print("\n🎯 正在训练模型...")

        # 划分训练集和测试集
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=0.2,
            random_state=42,
            stratify=y  # 分层采样，保持正负样本比例
        )

        print(f"   - 训练集大小: {len(X_train)}")
        print(f"   - 测试集大小: {len(X_test)}")

        # 创建 Random Forest 模型
        self.model = RandomForestClassifier(
            n_estimators=100,  # 树的数量
            max_depth=10,      # 最大深度
            min_samples_split=10,
            min_samples_leaf=5,
            random_state=42,
            n_jobs=-1,         # 使用所有 CPU 核心
            class_weight='balanced'  # 处理类别不平衡
        )

        # 训练模型
        self.model.fit(X_train, y_train)

        # 评估模型
        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)[:, 1]

        print("\n📈 模型评估结果:")
        print("-" * 60)

        # 基础指标
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_pred_proba)

        print(f"   准确率 (Accuracy):  {accuracy:.4f}")
        print(f"   精确率 (Precision): {precision:.4f}")
        print(f"   召回率 (Recall):     {recall:.4f}")
        print(f"   F1 分数:            {f1:.4f}")
        print(f"   AUC-ROC:            {auc:.4f}")

        print("\n" + "-" * 60)
        print("分类报告:")
        print(classification_report(y_test, y_pred, target_names=['未订阅', '订阅']))

        print("\n" + "-" * 60)
        print("混淆矩阵:")
        cm = confusion_matrix(y_test, y_pred)
        print(f"                  预测")
        print(f"              未订阅  订阅")
        print(f"实际 未订阅    {cm[0][0]:5d}  {cm[0][1]:5d}")
        print(f"     订阅      {cm[1][0]:5d}  {cm[1][1]:5d}")

        # 特征重要性
        feature_importance = pd.DataFrame({
            'feature': self.feature_names,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)

        print("\n" + "-" * 60)
        print("特征重要性 Top 10:")
        print(feature_importance.head(10).to_string(index=False))

        # 交叉验证
        print("\n" + "-" * 60)
        print("进行 5 折交叉验证...")
        cv_scores = cross_val_score(self.model, X, y, cv=5, scoring='accuracy')
        print(f"   交叉验证准确率: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")

        return self.model

    def save_model(self, output_dir: str = None):
        """
        保存训练好的模型和元数据

        Args:
            output_dir: 输出目录，默认为 data/models/
        """
        if output_dir is None:
            output_dir = Path(__file__).parent.parent.parent / "data" / "models"

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n💾 正在保存模型...")

        try:
            # 保存模型
            model_path = output_dir / "conversion_model.pkl"
            with open(model_path, 'wb') as f:
                pickle.dump(self.model, f)

            print(f"✅ 模型已保存: {model_path}")

            # 保存元数据
            metadata = {
                'model_type': 'RandomForestClassifier',
                'feature_names': self.feature_names,
                'training_date': datetime.now().isoformat(),
                'n_features': len(self.feature_names),
                'n_estimators': self.model.n_estimators,
                'max_depth': self.model.max_depth
            }

            metadata_path = output_dir / "conversion_model_metadata.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

            print(f"✅ 元数据已保存: {metadata_path}")

            # 保存 Label Encoders
            encoders_path = output_dir / "label_encoders.pkl"
            with open(encoders_path, 'wb') as f:
                pickle.dump(self.label_encoders, f)

            print(f"✅ 编码器已保存: {encoders_path}")

        except Exception as e:
            print(f"❌ 错误: 模型保存失败 - {str(e)}")

    def run(self):
        """执行完整的训练流程"""
        print("=" * 60)
        print("🤖 机器学习模型训练 - 银行营销转化预测")
        print("=" * 60)

        # 1. 加载数据
        df = self.load_data()
        if df is None:
            return False

        # 2. 数据预处理
        X, y = self.preprocess_data(df)

        # 3. 训练模型
        self.model = self.train_model(X, y)

        # 4. 保存模型
        self.save_model()

        print("\n" + "=" * 60)
        print("✅ 训练完成!")
        print("=" * 60)

        return True


def main():
    """主函数"""
    trainer = ModelTrainer()
    trainer.run()


if __name__ == "__main__":
    main()
