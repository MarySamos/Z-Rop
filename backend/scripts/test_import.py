"""
简化版数据导入测试
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from sqlalchemy import create_engine, text
from app.core.config import settings
from app.core.database import Base
from app.db.models import MarketingData

print("=" * 60)
print("🧪 简化版数据导入测试")
print("=" * 60)

# 1. 读取 CSV
csv_path = Path(__file__).parent.parent.parent / "data" / "raw" / "bank.csv"
print(f"\n📂 读取文件: {csv_path}")

df = pd.read_csv(csv_path, encoding='utf-8')
print(f"✅ 读取成功: {len(df)} 行, {len(df.columns)} 列")
print(f"列名: {list(df.columns)}")

# 2. 列名映射
print("\n🔧 列名映射...")
rename_map = {
    'default': 'default_credit',
    'deposit': 'y'
}
df = df.rename(columns=rename_map)
print(f"映射后列名: {list(df.columns)}")

# 3. 只保留前 10 行测试
df_test = df.head(10)
print(f"\n📊 测试数据: {len(df_test)} 行")
print(df_test.head())

# 4. 连接数据库
print("\n🔗 连接数据库...")
engine = create_engine(settings.DATABASE_URL)

# 5. 清空表
print("🗑️  清空表...")
with engine.connect() as conn:
    conn.execute(text("TRUNCATE TABLE marketing_data RESTART IDENTITY CASCADE"))
    conn.commit()

# 6. 导入数据
print("📥 导入数据...")
try:
    df_test.to_sql(
        'marketing_data',
        engine,
        if_exists='append',
        index=False,
        method='multi',
        chunksize=10
    )
    print("✅ 导入成功!")
    
    # 验证
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM marketing_data"))
        count = result.fetchone()[0]
        print(f"数据库中现有 {count} 条记录")
        
except Exception as e:
    import traceback
    print(f"❌ 导入失败!")
    print(f"错误: {e}")
    traceback.print_exc()

engine.dispose()
print("\n" + "=" * 60)
