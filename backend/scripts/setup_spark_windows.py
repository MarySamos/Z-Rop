"""
配置 Windows + PySpark 环境
下载并配置 Hadoop winutils
"""
import os
import sys
import shutil
from pathlib import Path


def setup_spark_for_windows():
    """为 Windows 配置 Spark + Hadoop winutils"""

    print("=" * 80)
    print("Windows + PySpark 环境配置工具")
    print("=" * 80)
    print()

    # 获取项目根目录
    project_root = Path(__file__).parent.parent.parent
    backend_dir = project_root / "backend"
    winutils_dir = backend_dir / "winutils"
    hadoop_version = "hadoop-3.2.2"  # PySpark 4.1.0 使用 Hadoop 3.2.x
    hadoop_home = winutils_dir / hadoop_version

    print(f"项目根目录: {project_root}")
    print(f"Hadoop 版本: {hadoop_version}")
    print(f"HADOOP_HOME: {hadoop_home}")
    print()

    # 检查 winutils 是否已下载
    if not hadoop_home.exists():
        print("[ERROR] winutils not found")
        print(f"   Please ensure directory exists: {hadoop_home}")
        return False

    # 检查 winutils.exe 是否存在
    winutils_exe = hadoop_home / "bin" / "winutils.exe"
    if not winutils_exe.exists():
        print(f"[ERROR] winutils.exe not found")
        print(f"   Expected location: {winutils_exe}")
        return False

    print(f"[OK] Found winutils.exe: {winutils_exe}")
    print()

    # 设置环境变量
    print("设置环境变量...")

    # HADOOP_HOME
    hadoop_home_str = str(hadoop_home)
    print(f"   HADOOP_HOME={hadoop_home_str}")

    # 添加到 PATH
    hadoop_bin = str(hadoop_home / "bin")
    print(f"   PATH+={hadoop_bin}")
    print()

    # 创建配置脚本
    bat_script = backend_dir / "set_spark_env.bat"
    with open(bat_script, 'w', encoding='utf-8') as f:
        f.write(f"""@echo off
REM Spark on Windows 环境变量设置脚本

set HADOOP_HOME={hadoop_home_str}
set PATH=%PATH%;%HADOOP_HOME%\\bin

echo Spark Windows 环境变量已设置
echo HADOOP_HOME=%HADOOP_HOME%
echo.
""")

    print(f"[OK] Created config script: {bat_script}")
    print()

    # 创建 Python 配置文件
    python_config = backend_dir / "spark_config.py"
    with open(python_config, 'w', encoding='utf-8') as f:
        f.write(f'''"""
Spark Windows 配置
在导入 PySpark 前运行此配置
"""
import os

# 设置 Hadoop 环境变量
os.environ['HADOOP_HOME'] = r'{hadoop_home_str}'
os.environ['PATH'] = os.environ.get('PATH', '') + ';' + r'{hadoop_bin}'

print("Spark Windows 环境变量已设置")
print(f"HADOOP_HOME={{os.environ['HADOOP_HOME']}}")
''')

    print(f"[OK] Created Python config: {python_config}")
    print()

    print("=" * 80)
    print("Configuration Complete!")
    print("=" * 80)
    print()
    print("使用方法:")
    print()
    print("1. 在 Python 中使用:")
    print(f"   from backend.spark_config import *")
    print("   from pyspark.sql import SparkSession")
    print()
    print("2. 或在命令行中先运行:")
    print(f"   {bat_script}")
    print()

    return True


if __name__ == "__main__":
    success = setup_spark_for_windows()
    sys.exit(0 if success else 1)
