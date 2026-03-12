"""
数据分析服务
提供统计分析、聚类分析、关联规则挖掘等功能
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from sqlalchemy import create_engine
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

from app.core.config import settings


class AnalysisService:
    """数据分析服务"""
    
    def __init__(self):
        self.engine = create_engine(settings.DATABASE_URL)
    
    def _load_data(self, table_name: str = "marketing_data") -> pd.DataFrame:
        """加载数据"""
        return pd.read_sql(f"SELECT * FROM {table_name}", self.engine)
    
    # ========== 统计分析 ==========
    
    def descriptive_statistics(self, columns: List[str] = None) -> Dict[str, Any]:
        """
        描述性统计分析
        
        Args:
            columns: 要分析的列，None 则分析所有数值列
        
        Returns:
            统计结果
        """
        df = self._load_data()
        
        # 选择数值列
        if columns:
            numeric_df = df[columns].select_dtypes(include=[np.number])
        else:
            numeric_df = df.select_dtypes(include=[np.number])
            numeric_df = numeric_df.drop(columns=['id'], errors='ignore')
        
        stats = {}
        
        for col in numeric_df.columns:
            series = numeric_df[col].dropna()
            
            stats[col] = {
                "count": int(len(series)),
                "mean": round(float(series.mean()), 2),
                "median": round(float(series.median()), 2),
                "std": round(float(series.std()), 2),
                "min": round(float(series.min()), 2),
                "max": round(float(series.max()), 2),
                "q25": round(float(series.quantile(0.25)), 2),
                "q75": round(float(series.quantile(0.75)), 2),
                "skewness": round(float(series.skew()), 4),
                "kurtosis": round(float(series.kurtosis()), 4)
            }
        
        return {
            "total_rows": len(df),
            "columns_analyzed": list(numeric_df.columns),
            "statistics": stats
        }
    
    def data_quality_report(self) -> Dict[str, Any]:
        """
        数据质量报告
        
        检测缺失值、异常值等
        """
        df = self._load_data()
        
        # 缺失值分析
        missing = df.isnull().sum()
        missing_pct = (missing / len(df) * 100).round(2)
        
        missing_report = {
            col: {
                "missing_count": int(missing[col]),
                "missing_percentage": float(missing_pct[col])
            }
            for col in df.columns if missing[col] > 0
        }
        
        # 异常值检测（3σ法则）
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        numeric_cols = [c for c in numeric_cols if c != 'id']
        
        outliers = {}
        for col in numeric_cols:
            series = df[col].dropna()
            mean = series.mean()
            std = series.std()
            
            lower = mean - 3 * std
            upper = mean + 3 * std
            
            outlier_count = ((series < lower) | (series > upper)).sum()
            
            if outlier_count > 0:
                outliers[col] = {
                    "outlier_count": int(outlier_count),
                    "outlier_percentage": round(outlier_count / len(series) * 100, 2),
                    "lower_bound": round(float(lower), 2),
                    "upper_bound": round(float(upper), 2)
                }
        
        # 数据类型分布
        dtype_counts = df.dtypes.astype(str).value_counts().to_dict()
        
        return {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "missing_values": missing_report,
            "total_missing_cells": int(missing.sum()),
            "outliers_3sigma": outliers,
            "data_types": dtype_counts,
            "completeness": round((1 - missing.sum() / (len(df) * len(df.columns))) * 100, 2)
        }
    
    def correlation_analysis(self, method: str = "pearson") -> Dict[str, Any]:
        """
        相关性分析
        
        Args:
            method: 相关系数类型 (pearson, spearman, kendall)
        """
        df = self._load_data()
        
        # 选择数值列
        numeric_df = df.select_dtypes(include=[np.number])
        numeric_df = numeric_df.drop(columns=['id'], errors='ignore')
        
        # 计算相关系数矩阵
        corr_matrix = numeric_df.corr(method=method)
        
        # 转换为前端友好格式
        correlations = []
        columns = list(corr_matrix.columns)
        
        for i, col1 in enumerate(columns):
            for j, col2 in enumerate(columns):
                if i < j:  # 只取上三角
                    correlations.append({
                        "var1": col1,
                        "var2": col2,
                        "correlation": round(float(corr_matrix.loc[col1, col2]), 4)
                    })
        
        # 按相关性绝对值排序
        correlations.sort(key=lambda x: abs(x["correlation"]), reverse=True)
        
        # 热力图数据
        heatmap_data = []
        for i, col1 in enumerate(columns):
            for j, col2 in enumerate(columns):
                heatmap_data.append([i, j, round(float(corr_matrix.loc[col1, col2]), 2)])
        
        return {
            "method": method,
            "columns": columns,
            "top_correlations": correlations[:15],
            "heatmap_data": heatmap_data,
            "matrix": corr_matrix.round(4).to_dict()
        }
    
    def distribution_analysis(self, column: str) -> Dict[str, Any]:
        """
        单变量分布分析
        """
        df = self._load_data()
        
        if column not in df.columns:
            return {"error": f"列 {column} 不存在"}
        
        series = df[column].dropna()
        
        if series.dtype in [np.int64, np.float64]:
            # 数值型：分箱统计
            bins = min(20, series.nunique())
            hist, edges = np.histogram(series, bins=bins)
            
            return {
                "column": column,
                "type": "numeric",
                "count": int(len(series)),
                "unique": int(series.nunique()),
                "histogram": {
                    "bins": [round(float(e), 2) for e in edges],
                    "counts": [int(h) for h in hist]
                },
                "statistics": {
                    "mean": round(float(series.mean()), 2),
                    "median": round(float(series.median()), 2),
                    "std": round(float(series.std()), 2)
                }
            }
        else:
            # 分类型：值计数
            value_counts = series.value_counts().head(20)
            
            return {
                "column": column,
                "type": "categorical",
                "count": int(len(series)),
                "unique": int(series.nunique()),
                "value_counts": {
                    "labels": value_counts.index.tolist(),
                    "values": value_counts.values.tolist()
                }
            }
    
    # ========== 聚类分析 ==========
    
    def clustering_analysis(
        self,
        n_clusters: int = None,
        features: List[str] = None,
        max_k: int = 10
    ) -> Dict[str, Any]:
        """
        K-Means 聚类分析
        
        Args:
            n_clusters: 聚类数量，None 则自动选择
            features: 用于聚类的特征列表
            max_k: 自动选择时的最大 K 值
        
        Returns:
            聚类结果和分析
        """
        print("🔍 开始聚类分析...")
        
        # 加载数据
        df = self._load_data()
        
        # 默认特征
        if features is None:
            features = ['age', 'balance', 'duration', 'campaign', 'pdays', 'previous']
        
        # 只保留可用特征
        available_features = [f for f in features if f in df.columns]
        
        # 准备数据
        X = df[available_features].copy()
        
        # 处理缺失值
        X = X.fillna(X.median())
        
        # 标准化
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # 自动选择最优 K 值
        if n_clusters is None:
            n_clusters, elbow_data = self._find_optimal_k(X_scaled, max_k)
        else:
            elbow_data = None
        
        # 执行聚类
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(X_scaled)
        
        # 计算轮廓系数
        silhouette = silhouette_score(X_scaled, clusters)
        
        # 添加聚类标签到原数据
        df['cluster'] = clusters
        
        # 生成客户画像
        profiles = self._generate_cluster_profiles(df, available_features)
        
        # 聚类分布
        cluster_distribution = df['cluster'].value_counts().sort_index().to_dict()
        
        # 聚类中心（反标准化）
        centers = scaler.inverse_transform(kmeans.cluster_centers_)
        cluster_centers = []
        for i, center in enumerate(centers):
            cluster_centers.append({
                "cluster": i,
                **{f: round(float(v), 2) for f, v in zip(available_features, center)}
            })
        
        return {
            "n_clusters": n_clusters,
            "features_used": available_features,
            "silhouette_score": round(float(silhouette), 4),
            "cluster_distribution": cluster_distribution,
            "cluster_centers": cluster_centers,
            "cluster_profiles": profiles,
            "elbow_data": elbow_data
        }
    
    def _find_optimal_k(self, X: np.ndarray, max_k: int = 10) -> tuple:
        """
        使用肘部法则找最优 K 值
        """
        inertias = []
        silhouettes = []
        k_range = range(2, min(max_k + 1, len(X)))
        
        for k in k_range:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            kmeans.fit(X)
            inertias.append(kmeans.inertia_)
            silhouettes.append(silhouette_score(X, kmeans.labels_))
        
        # 简单的肘部检测：找二阶导数最大的点
        if len(inertias) > 2:
            diffs = np.diff(inertias)
            diffs2 = np.diff(diffs)
            optimal_idx = np.argmax(np.abs(diffs2)) + 2
            optimal_k = list(k_range)[min(optimal_idx, len(k_range) - 1)]
        else:
            optimal_k = 3
        
        # 但也参考轮廓系数
        best_silhouette_idx = np.argmax(silhouettes)
        if silhouettes[best_silhouette_idx] > 0.3:  # 如果轮廓系数足够好
            optimal_k = list(k_range)[best_silhouette_idx]
        
        elbow_data = {
            "k_values": list(k_range),
            "inertias": [round(float(i), 2) for i in inertias],
            "silhouettes": [round(float(s), 4) for s in silhouettes],
            "optimal_k": optimal_k
        }
        
        return optimal_k, elbow_data
    
    def _generate_cluster_profiles(
        self, 
        df: pd.DataFrame, 
        features: List[str]
    ) -> List[Dict[str, Any]]:
        """
        生成每个聚类的客户画像
        """
        profiles = []
        
        for cluster_id in sorted(df['cluster'].unique()):
            cluster_df = df[df['cluster'] == cluster_id]
            
            profile = {
                "cluster_id": int(cluster_id),
                "size": len(cluster_df),
                "percentage": round(len(cluster_df) / len(df) * 100, 1),
                "characteristics": {}
            }
            
            # 数值特征统计
            for feat in features:
                if feat in cluster_df.columns:
                    profile["characteristics"][feat] = {
                        "mean": round(float(cluster_df[feat].mean()), 2),
                        "median": round(float(cluster_df[feat].median()), 2)
                    }
            
            # 转化率
            if 'y' in cluster_df.columns:
                conversion = (cluster_df['y'] == 'yes').mean() * 100
                profile["conversion_rate"] = round(conversion, 2)
            
            # 主要职业
            if 'job' in cluster_df.columns:
                top_job = cluster_df['job'].mode()
                profile["dominant_job"] = top_job.iloc[0] if len(top_job) > 0 else "unknown"
            
            # 主要婚姻状况
            if 'marital' in cluster_df.columns:
                top_marital = cluster_df['marital'].mode()
                profile["dominant_marital"] = top_marital.iloc[0] if len(top_marital) > 0 else "unknown"
            
            # 生成描述标签
            profile["label"] = self._generate_cluster_label(profile)
            
            profiles.append(profile)
        
        return profiles
    
    def _generate_cluster_label(self, profile: Dict) -> str:
        """根据特征生成聚类标签"""
        chars = profile.get("characteristics", {})
        
        age_mean = chars.get("age", {}).get("mean", 0)
        balance_mean = chars.get("balance", {}).get("mean", 0)
        conversion = profile.get("conversion_rate", 0)
        
        labels = []
        
        # 年龄标签
        if age_mean < 30:
            labels.append("年轻")
        elif age_mean > 50:
            labels.append("中老年")
        else:
            labels.append("中年")
        
        # 余额标签
        if balance_mean > 2000:
            labels.append("高净值")
        elif balance_mean < 500:
            labels.append("低余额")
        else:
            labels.append("中等余额")
        
        # 转化标签
        if conversion > 20:
            labels.append("高转化")
        elif conversion < 10:
            labels.append("低转化")
        
        return " + ".join(labels) if labels else f"群体 {profile['cluster_id']}"
    
    # ========== 关联规则挖掘 ==========
    
    def association_rules(
        self,
        min_support: float = 0.1,
        min_confidence: float = 0.5,
        max_rules: int = 20
    ) -> Dict[str, Any]:
        """
        Apriori 关联规则挖掘
        
        发现特征之间的关联模式，如 "高学历 + 已婚 -> 高转化"
        
        Args:
            min_support: 最小支持度
            min_confidence: 最小置信度
            max_rules: 最大返回规则数
        """
        try:
            from mlxtend.frequent_patterns import apriori, association_rules as ar
            from mlxtend.preprocessing import TransactionEncoder
        except ImportError:
            return {"error": "需要安装 mlxtend 库: pip install mlxtend"}
        
        df = self._load_data()
        
        # 将数据转换为事务格式（离散化）
        transactions = []
        
        for _, row in df.iterrows():
            items = []
            
            # 年龄分组
            if row.get('age'):
                if row['age'] < 30:
                    items.append('年龄:青年')
                elif row['age'] < 50:
                    items.append('年龄:中年')
                else:
                    items.append('年龄:老年')
            
            # 职业
            if row.get('job'):
                items.append(f"职业:{row['job']}")
            
            # 婚姻状况
            if row.get('marital'):
                items.append(f"婚姻:{row['marital']}")
            
            # 教育程度
            if row.get('education'):
                items.append(f"教育:{row['education']}")
            
            # 余额分组
            if row.get('balance') is not None:
                if row['balance'] < 0:
                    items.append('余额:负债')
                elif row['balance'] < 1000:
                    items.append('余额:低')
                elif row['balance'] < 5000:
                    items.append('余额:中')
                else:
                    items.append('余额:高')
            
            # 贷款情况
            if row.get('housing') == 'yes':
                items.append('有房贷')
            if row.get('loan') == 'yes':
                items.append('有个人贷款')
            
            # 目标变量
            if row.get('y') == 'yes':
                items.append('已转化')
            else:
                items.append('未转化')
            
            transactions.append(items)
        
        # 转换为 one-hot 编码
        te = TransactionEncoder()
        te_ary = te.fit_transform(transactions)
        df_encoded = pd.DataFrame(te_ary, columns=te.columns_)
        
        # Apriori 算法找频繁项集
        frequent_itemsets = apriori(
            df_encoded, 
            min_support=min_support, 
            use_colnames=True
        )
        
        if len(frequent_itemsets) == 0:
            return {
                "error": "未找到频繁项集，请降低 min_support 阈值",
                "min_support": min_support
            }
        
        # 生成关联规则
        rules = ar(
            frequent_itemsets, 
            metric="confidence", 
            min_threshold=min_confidence
        )
        
        if len(rules) == 0:
            return {
                "error": "未找到关联规则，请降低 min_confidence 阈值",
                "min_confidence": min_confidence
            }
        
        # 按提升度排序
        rules = rules.sort_values('lift', ascending=False).head(max_rules)
        
        # 格式化输出
        rules_list = []
        for _, rule in rules.iterrows():
            rules_list.append({
                "antecedents": list(rule['antecedents']),
                "consequents": list(rule['consequents']),
                "support": round(float(rule['support']), 4),
                "confidence": round(float(rule['confidence']), 4),
                "lift": round(float(rule['lift']), 4)
            })
        
        return {
            "total_frequent_itemsets": len(frequent_itemsets),
            "total_rules": len(rules_list),
            "min_support": min_support,
            "min_confidence": min_confidence,
            "rules": rules_list
        }
    
    # ========== 特征工程 ==========
    
    def feature_importance(self) -> Dict[str, Any]:
        """
        使用 Random Forest 计算特征重要性
        """
        from sklearn.ensemble import RandomForestClassifier
        
        df = self._load_data()
        
        # 准备数据
        feature_cols = ['age', 'balance', 'day', 'duration', 'campaign', 'pdays', 'previous']
        available_cols = [c for c in feature_cols if c in df.columns]
        
        X = df[available_cols].fillna(0)
        y = (df['y'] == 'yes').astype(int)
        
        # 训练模型
        rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
        rf.fit(X, y)
        
        # 获取特征重要性
        importances = rf.feature_importances_
        
        result = sorted(
            zip(available_cols, importances),
            key=lambda x: x[1],
            reverse=True
        )
        
        return {
            "features": [{"name": f, "importance": round(float(i), 4)} for f, i in result],
            "method": "RandomForest"
        }
    
    def pca_analysis(self, n_components: int = 2) -> Dict[str, Any]:
        """
        PCA 降维分析
        
        Args:
            n_components: 降维后的维度数
        """
        from sklearn.decomposition import PCA
        
        df = self._load_data()
        
        # 选择数值列
        numeric_cols = ['age', 'balance', 'day', 'duration', 'campaign', 'pdays', 'previous']
        available_cols = [c for c in numeric_cols if c in df.columns]
        
        X = df[available_cols].fillna(0)
        
        # 标准化
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # PCA
        pca = PCA(n_components=min(n_components, len(available_cols)))
        X_pca = pca.fit_transform(X_scaled)
        
        # 方差解释率
        explained_variance = pca.explained_variance_ratio_
        
        # 主成分载荷
        loadings = []
        for i, component in enumerate(pca.components_):
            loading = {
                "component": f"PC{i+1}",
                "variance_ratio": round(float(explained_variance[i]), 4),
                "loadings": {
                    col: round(float(val), 4) 
                    for col, val in zip(available_cols, component)
                }
            }
            loadings.append(loading)
        
        # 散点图数据（取前1000个点）
        sample_size = min(1000, len(X_pca))
        indices = np.random.choice(len(X_pca), sample_size, replace=False)
        
        scatter_data = []
        for idx in indices:
            point = {"x": round(float(X_pca[idx][0]), 4)}
            if n_components >= 2:
                point["y"] = round(float(X_pca[idx][1]), 4)
            point["label"] = df['y'].iloc[idx]
            scatter_data.append(point)
        
        return {
            "n_components": pca.n_components_,
            "total_variance_explained": round(float(sum(explained_variance)), 4),
            "components": loadings,
            "scatter_data": scatter_data
        }

    # ========== 时间序列分析 ==========

    def time_series_analysis(self) -> Dict[str, Any]:
        """
        时间序列趋势分析

        按月份统计客户数、转化率等指标，并计算移动平均预测
        """
        df = self._load_data()

        # 月份排序映射
        month_order = {
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
            'may': 5, 'jun': 6, 'jul': 7, 'aug': 8,
            'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
        }

        if 'month' not in df.columns:
            return {"error": "数据中缺少 month 列"}

        # 按月份聚合统计
        monthly = df.groupby('month').agg(
            customer_count=('id', 'count'),
            avg_age=('age', 'mean'),
            avg_balance=('balance', lambda x: x.mean() if x.notna().any() else 0),
            avg_duration=('duration', 'mean'),
            conversion_count=('y', lambda x: (x == 'yes').sum()),
            total_count=('y', 'count')
        ).reset_index()

        # 计算转化率
        monthly['conversion_rate'] = (
            monthly['conversion_count'] / monthly['total_count'] * 100
        ).round(2)

        # 添加月份排序号
        monthly['month_num'] = monthly['month'].str.lower().map(month_order)
        monthly = monthly.sort_values('month_num').reset_index(drop=True)

        # 月份标签
        month_labels = monthly['month'].str.capitalize().tolist()

        # 客户数趋势
        customer_counts = monthly['customer_count'].tolist()

        # 转化率趋势
        conversion_rates = monthly['conversion_rate'].tolist()

        # 平均余额趋势
        avg_balances = [round(float(b), 2) for b in monthly['avg_balance']]

        # 移动平均预测（3月窗口）
        customer_series = pd.Series(customer_counts)
        ma_3 = customer_series.rolling(window=3, min_periods=1).mean().round(0).astype(int).tolist()

        conversion_series = pd.Series(conversion_rates)
        ma_conversion = conversion_series.rolling(window=3, min_periods=1).mean().round(2).tolist()

        return {
            "months": month_labels,
            "customer_count": {
                "values": customer_counts,
                "moving_avg": ma_3
            },
            "conversion_rate": {
                "values": conversion_rates,
                "moving_avg": ma_conversion
            },
            "avg_balance": avg_balances,
            "avg_duration": [round(float(d), 1) for d in monthly['avg_duration']],
            "summary": {
                "total_months": len(month_labels),
                "peak_month": month_labels[int(np.argmax(customer_counts))],
                "peak_count": int(max(customer_counts)),
                "best_conversion_month": month_labels[int(np.argmax(conversion_rates))],
                "best_conversion_rate": float(max(conversion_rates))
            }
        }

    # ========== 漏斗分析 ==========

    def funnel_analysis(self) -> Dict[str, Any]:
        """
        营销漏斗分析

        计算营销各环节的转化率和流失率：
        总客户 → 有效联系（duration > 0） → 深度沟通（duration > 120s）
        → 多次跟进（campaign > 1） → 最终转化（y = yes）
        """
        df = self._load_data()

        total = len(df)

        # 第1层：总客户数
        # 第2层：有效联系（通话时长 > 0）
        contacted = len(df[df['duration'] > 0])

        # 第3层：深度沟通（通话时长 > 120秒 = 2分钟）
        deep_contact = len(df[df['duration'] > 120])

        # 第4层：多次跟进（本次活动联系次数 > 1）
        multi_follow = len(df[(df['duration'] > 0) & (df['campaign'] > 1)])

        # 第5层：最终转化（y = yes）
        converted = len(df[df['y'] == 'yes'])

        # 构建漏斗数据
        stages = [
            {
                "name": "总客户池",
                "count": total,
                "rate": 100.0,
                "drop_rate": 0.0
            },
            {
                "name": "有效联系",
                "count": contacted,
                "rate": round(contacted / total * 100, 2) if total > 0 else 0,
                "drop_rate": round((total - contacted) / total * 100, 2) if total > 0 else 0
            },
            {
                "name": "深度沟通 (>2min)",
                "count": deep_contact,
                "rate": round(deep_contact / total * 100, 2) if total > 0 else 0,
                "drop_rate": round((contacted - deep_contact) / contacted * 100, 2) if contacted > 0 else 0
            },
            {
                "name": "多次跟进",
                "count": multi_follow,
                "rate": round(multi_follow / total * 100, 2) if total > 0 else 0,
                "drop_rate": round((deep_contact - multi_follow) / deep_contact * 100, 2) if deep_contact > 0 else 0
            },
            {
                "name": "最终转化",
                "count": converted,
                "rate": round(converted / total * 100, 2) if total > 0 else 0,
                "drop_rate": round((multi_follow - converted) / multi_follow * 100, 2) if multi_follow > 0 else 0
            }
        ]

        # 按转化结果分析各维度
        converted_df = df[df['y'] == 'yes']
        not_converted_df = df[df['y'] == 'no']

        comparison = {
            "avg_duration": {
                "converted": round(float(converted_df['duration'].mean()), 1) if len(converted_df) > 0 else 0,
                "not_converted": round(float(not_converted_df['duration'].mean()), 1) if len(not_converted_df) > 0 else 0
            },
            "avg_campaign": {
                "converted": round(float(converted_df['campaign'].mean()), 2) if len(converted_df) > 0 else 0,
                "not_converted": round(float(not_converted_df['campaign'].mean()), 2) if len(not_converted_df) > 0 else 0
            }
        }

        if 'balance' in df.columns and df['balance'].notna().any():
            comparison["avg_balance"] = {
                "converted": round(float(converted_df['balance'].mean()), 2) if len(converted_df) > 0 else 0,
                "not_converted": round(float(not_converted_df['balance'].mean()), 2) if len(not_converted_df) > 0 else 0
            }

        return {
            "total_customers": total,
            "total_converted": converted,
            "overall_conversion_rate": round(converted / total * 100, 2) if total > 0 else 0,
            "stages": stages,
            "comparison": comparison
        }


# 全局服务实例
analysis_service = AnalysisService()

