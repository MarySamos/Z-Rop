"""
测试数据库连接
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from app.core.config import settings

print("=" * 60)
print("🔍 测试数据库连接")
print("=" * 60)

print(f"\n数据库 URL: {settings.DATABASE_URL[:50]}...")

try:
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        version = result.fetchone()[0]
        print(f"\n✅ 连接成功!")
        print(f"PostgreSQL 版本: {version[:80]}")
        
        # 测试查询表
        result = conn.execute(text("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public'
        """))
        tables = [row[0] for row in result.fetchall()]
        print(f"\n📋 现有表: {tables}")
        
except Exception as e:
    print(f"\n❌ 连接失败!")
    print(f"错误信息: {str(e)}")
    print("\n💡 请检查:")
    print("  1. PostgreSQL 服务是否启动")
    print("  2. .env 文件中的 DATABASE_URL 是否正确")
    print("  3. 数据库 'bank_agent' 是否已创建")

print("\n" + "=" * 60)
