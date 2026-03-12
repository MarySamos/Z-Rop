"""
重建 marketing_data 表
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from app.core.config import settings
from app.core.database import Base
from app.db.models import MarketingData

print("=" * 60)
print("🔨 重建 marketing_data 表")
print("=" * 60)

engine = create_engine(settings.DATABASE_URL)

print("\n1️⃣ 删除旧表...")
with engine.connect() as conn:
    conn.execute(text("DROP TABLE IF EXISTS marketing_data CASCADE"))
    conn.commit()
print("   ✅ 旧表已删除")

print("\n2️⃣ 创建新表...")
Base.metadata.create_all(bind=engine, tables=[MarketingData.__table__])
print("   ✅ 新表已创建")

print("\n3️⃣ 验证表结构...")
from sqlalchemy import inspect
inspector = inspect(engine)
columns = inspector.get_columns('marketing_data')
print(f"   表中的列 ({len(columns)} 个):")
for col in columns:
    print(f"     - {col['name']}")

engine.dispose()
print("\n" + "=" * 60)
print("✅ 表重建完成!")
print("=" * 60)
