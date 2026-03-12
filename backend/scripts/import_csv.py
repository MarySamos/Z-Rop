"""
银行营销数据导入工具 (优化版)

功能:
    1. 自动检测 CSV 文件格式（分号/逗号分隔）
    2. 自动映射 Kaggle 数据集列名到数据库字段
    3. 支持增量导入或全量替换
    4. 数据质量检查与报告

使用方法:
    cd backend
    python scripts/import_csv.py                    # 使用默认路径
    python scripts/import_csv.py <csv_file_path>   # 指定文件路径

Kaggle 数据集: https://www.kaggle.com/datasets/henriqueyamahata/bank-marketing
"""
import sys
import os
from pathlib import Path
from typing import Optional

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.database import Base
from app.db.models import MarketingData


# Kaggle Bank Marketing 数据集的列名映射
# 支持旧版 (bank.csv) 和新版 (bank-additional-full.csv)
COLUMN_MAPPING = {
    # 基础字段
    'age': 'age',
    'job': 'job',
    'marital': 'marital',
    'education': 'education',
    'default': 'default_credit',      # 'default' 是 SQL 保留字，重命名
    'balance': 'balance',             # 旧版数据集特有
    'housing': 'housing',
    'loan': 'loan',
    'contact': 'contact',
    'day': 'day',                     # 旧版数据集：联系日期
    'month': 'month',
    'day_of_week': 'day_of_week',     # 新版数据集：联系星期
    'duration': 'duration',
    'campaign': 'campaign',
    'pdays': 'pdays',
    'previous': 'previous',
    'poutcome': 'poutcome',
    # 经济指标（新版数据集特有）
    'emp.var.rate': 'emp_var_rate',
    'cons.price.idx': 'cons_price_idx',
    'cons.conf.idx': 'cons_conf_idx',
    'euribor3m': 'euribor3m',
    'nr.employed': 'nr_employed',
    # 目标变量（两个版本名称不同）
    'deposit': 'y',                   # 旧版数据集：deposit -> y
    'y': 'y'                          # 新版数据集：y -> y
}


def detect_csv_separator(file_path: str) -> str:
    """
    自动检测 CSV 文件的分隔符

    Args:
        file_path: CSV 文件路径

    Returns:
        分隔符字符 (',' 或 ';')
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        first_line = f.readline()
        # 统计分号和逗号的数量
        semicolon_count = first_line.count(';')
        comma_count = first_line.count(',')
        return ';' if semicolon_count > comma_count else ','


def load_and_validate_csv(csv_file_path: str) -> Optional[pd.DataFrame]:
    """
    加载并验证 CSV 文件

    Args:
        csv_file_path: CSV 文件路径

    Returns:
        DataFrame 或 None（如果失败）
    """
    print(f"📂 正在读取 CSV 文件: {csv_file_path}")

    if not Path(csv_file_path).exists():
        print(f"❌ 错误: CSV 文件不存在: {csv_file_path}")
        print("\n💡 提示: 请从 Kaggle 下载数据集并放入 data/raw/ 目录")
        print("   下载地址: https://www.kaggle.com/datasets/henriqueyamahata/bank-marketing")
        return None

    try:
        # 自动检测分隔符
        separator = detect_csv_separator(csv_file_path)
        print(f"   检测到分隔符: '{separator}'")

        # 读取 CSV 文件，明确指定编码
        df = pd.read_csv(csv_file_path, sep=separator, encoding='utf-8')

        print(f"✅ CSV 文件读取成功!")
        print(f"   - 数据行数: {len(df):,}")
        print(f"   - 数据列数: {len(df.columns)}")
        print(f"   - 原始列名: {list(df.columns)}")

        return df

    except pd.errors.EmptyDataError:
        print(f"❌ 错误: CSV 文件为空")
        return None
    except pd.errors.ParserError as e:
        print(f"❌ 错误: CSV 文件解析失败 - {str(e)}")
        return None
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        return None


def preprocess_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    预处理 DataFrame，进行列名映射和数据清洗

    Args:
        df: 原始 DataFrame

    Returns:
        预处理后的 DataFrame
    """
    print("\n🔧 正在预处理数据...")

    # 1. 列名映射（兼容不同格式的 Kaggle 数据集）
    df_processed = df.copy()
    rename_map = {}

    for old_name, new_name in COLUMN_MAPPING.items():
        if old_name in df_processed.columns:
            rename_map[old_name] = new_name

    if rename_map:
        df_processed = df_processed.rename(columns=rename_map)
        print(f"   ✅ 列名映射完成: {len(rename_map)} 列")

    # 2. 只保留数据库模型中定义的列
    valid_columns = [
        'age', 'job', 'marital', 'education', 'default_credit',
        'balance', 'housing', 'loan', 'contact', 'day', 'month', 'day_of_week',
        'duration', 'campaign', 'pdays', 'previous', 'poutcome',
        'emp_var_rate', 'cons_price_idx', 'cons_conf_idx',
        'euribor3m', 'nr_employed', 'y'
    ]

    existing_columns = [col for col in valid_columns if col in df_processed.columns]
    df_processed = df_processed[existing_columns]
    print(f"   ✅ 保留有效列: {len(existing_columns)} 列")

    # 3. 数据类型转换
    # 确保数值类型正确
    numeric_int_cols = ['age', 'balance', 'day', 'duration', 'campaign', 'pdays', 'previous']
    numeric_float_cols = ['emp_var_rate', 'cons_price_idx', 'cons_conf_idx', 'euribor3m', 'nr_employed']

    for col in numeric_int_cols:
        if col in df_processed.columns:
            df_processed[col] = pd.to_numeric(df_processed[col], errors='coerce').fillna(0).astype(int)

    for col in numeric_float_cols:
        if col in df_processed.columns:
            df_processed[col] = pd.to_numeric(df_processed[col], errors='coerce')

    print(f"   ✅ 数据类型转换完成")

    return df_processed


def data_quality_report(df: pd.DataFrame) -> None:
    """
    生成数据质量报告

    Args:
        df: DataFrame
    """
    print("\n📊 数据质量报告:")
    print("-" * 50)

    # 缺失值检查
    missing_counts = df.isnull().sum()
    if missing_counts.sum() > 0:
        print("⚠️  缺失值统计:")
        for col, count in missing_counts[missing_counts > 0].items():
            pct = count / len(df) * 100
            print(f"   - {col}: {count:,} ({pct:.2f}%)")
    else:
        print("✅ 没有缺失值")

    # 目标变量分布（如果存在）
    if 'y' in df.columns:
        print("\n📈 目标变量 (y) 分布:")
        y_counts = df['y'].value_counts()
        for value, count in y_counts.items():
            pct = count / len(df) * 100
            print(f"   - {value}: {count:,} ({pct:.2f}%)")

    # 数据预览
    print("\n📋 数据预览 (前 5 行):")
    print(df.head().to_string())
    print("-" * 50)


def import_to_database(df: pd.DataFrame, mode: str = 'replace') -> bool:
    """
    将 DataFrame 导入到 PostgreSQL 数据库

    Args:
        df: 预处理后的 DataFrame
        mode: 'replace' (全量替换) 或 'append' (增量追加)

    Returns:
        是否成功
    """
    print(f"\n🔗 正在连接数据库...")

    try:
        engine = create_engine(settings.DATABASE_URL)

        # 确保表存在（使用 SQLAlchemy 模型创建）
        Base.metadata.create_all(bind=engine, tables=[MarketingData.__table__])

        if mode == 'replace':
            # 先清空表，再插入
            with engine.connect() as conn:
                conn.execute(text("TRUNCATE TABLE marketing_data RESTART IDENTITY CASCADE"))
                conn.commit()
            print(f"   ✅ 已清空 marketing_data 表")

        # 使用 to_sql 批量插入数据
        print(f"📥 正在导入数据到 marketing_data 表 (模式: {mode})...")

        df.to_sql(
            'marketing_data',
            engine,
            if_exists='append',  # 使用 append 因为表结构已存在
            index=False,
            method='multi',
            chunksize=1000
        )

        # 验证导入结果
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM marketing_data"))
            count = result.fetchone()[0]
            print(f"\n✅ 数据导入成功!")
            print(f"   - 本次导入: {len(df):,} 条记录")
            print(f"   - 数据库总计: {count:,} 条记录")

        return True

    except Exception as e:
        import traceback
        print(f"❌ 数据库导入失败!")
        print(f"\n错误类型: {type(e).__name__}")
        print(f"错误信息: {str(e)}")
        print(f"\n完整堆栈:")
        traceback.print_exc()
        return False
    finally:
        if 'engine' in locals():
            engine.dispose()


def main():
    """主函数"""
    print("=" * 60)
    print("🏦 银行营销数据导入工具 (优化版)")
    print("=" * 60)

    # 获取 CSV 文件路径
    if len(sys.argv) > 1:
        csv_file_path = sys.argv[1]
    else:
        # 默认路径：支持多种常见文件名
        data_dir = Path(__file__).parent.parent.parent / "data" / "raw"
        possible_names = [
            "bank-marketing.csv",
            "bank-additional-full.csv",
            "bank-additional.csv",
            "bank-full.csv",
            "bank.csv"
        ]
        csv_file_path = None
        for name in possible_names:
            path = data_dir / name
            if path.exists():
                csv_file_path = str(path)
                break

        if csv_file_path is None:
            print(f"❌ 在 {data_dir} 目录下未找到数据文件")
            print(f"\n💡 请将 Kaggle 下载的 CSV 文件放入 data/raw/ 目录")
            print(f"   支持的文件名: {possible_names}")
            print("=" * 60)
            return

    # 步骤 1: 加载并验证 CSV 文件
    df = load_and_validate_csv(csv_file_path)
    if df is None:
        print("=" * 60)
        return

    # 步骤 2: 预处理数据
    df_processed = preprocess_dataframe(df)

    # 步骤 3: 数据质量报告
    data_quality_report(df_processed)

    # 步骤 4: 导入到数据库
    success = import_to_database(df_processed, mode='replace')

    print("\n" + "=" * 60)
    if success:
        print("✅ 数据导入完成! 现在可以运行 Text-to-SQL 智能问答了。")
    else:
        print("❌ 数据导入失败，请检查数据库连接和日志。")
    print("=" * 60)


if __name__ == "__main__":
    main()
