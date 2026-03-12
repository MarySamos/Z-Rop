"""
下载 PostgreSQL JDBC 驱动
用于 Spark 连接 PostgreSQL 数据库
"""
import os
import urllib.request
import zipfile
from pathlib import Path


def download_postgresql_jdbc():
    """下载 PostgreSQL JDBC 驱动到 libs 目录"""

    # JDBC 驱动版本和下载链接
    JDBC_VERSION = "42.7.4"
    JDBC_URL = f"https://jdbc.postgresql.org/download/postgresql-{JDBC_VERSION}.jar"

    # 创建 libs 目录
    libs_dir = Path(__file__).parent.parent / "libs"
    libs_dir.mkdir(exist_ok=True)

    jdbc_jar_path = libs_dir / f"postgresql-{JDBC_VERSION}.jar"

    print(f"📦 准备下载 PostgreSQL JDBC Driver {JDBC_VERSION}...")
    print(f"📁 保存位置: {jdbc_jar_path}")

    # 检查是否已存在
    if jdbc_jar_path.exists():
        print(f"✅ JDBC 驱动已存在: {jdbc_jar_path}")
        return str(jdbc_jar_path)

    try:
        # 下载文件
        print(f"⬇️  正在从 PostgreSQL 官方下载...")
        urllib.request.urlretrieve(JDBC_URL, jdbc_jar_path)

        print(f"✅ 下载成功: {jdbc_jar_path}")
        print(f"📊 文件大小: {jdbc_jar_path.stat().st_size / 1024 / 1024:.2f} MB")

        return str(jdbc_jar_path)

    except Exception as e:
        print(f"❌ 下载失败: {e}")
        print(f"\n💡 手动下载方法:")
        print(f"   1. 访问: {JDBC_URL}")
        print(f"   2. 将下载的 jar 文件放到: {libs_dir}")
        raise


if __name__ == "__main__":
    print("=" * 60)
    print("PostgreSQL JDBC Driver 下载工具")
    print("=" * 60)
    print()

    try:
        jar_path = download_postgresql_jdbc()
        print()
        print("=" * 60)
        print("🎉 JDBC 驱动安装完成！")
        print("=" * 60)
        print()
        print("接下来可以运行 Spark 基准测试：")
        print("  - 启动后端服务: cd backend && python -m uvicorn app.main:app --reload")
        print("  - 访问: http://localhost:8000/docs")
        print("  - 调用 POST /api/bigdata/benchmark 接口")
        print()

    except Exception as e:
        print()
        print("=" * 60)
        print("❌ 安装失败")
        print("=" * 60)
        exit(1)
