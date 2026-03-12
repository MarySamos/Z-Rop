"""
检查数据库表结构
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text, inspect
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
inspector = inspect(engine)

print("=" * 60)
print("📋 marketing_data 表结构")
print("=" * 60)

columns = inspector.get_columns('marketing_data')
print(f"\n表中的列 ({len(columns)} 个):")
for col in columns:
    nullable = "NULL" if col['nullable'] else "NOT NULL"
    print(f"  - {col['name']:<20} {str(col['type']):<15} {nullable}")

engine.dispose()
