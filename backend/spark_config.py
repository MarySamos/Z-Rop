"""
Spark Windows 配置
在导入 PySpark 前运行此配置
"""
import os

# 设置 Hadoop 环境变量
os.environ['HADOOP_HOME'] = r'G:\PycharmProjects\BankAgent-Pro\backend\winutils\hadoop-3.2.2'
os.environ['PATH'] = os.environ.get('PATH', '') + ';' + r'G:\PycharmProjects\BankAgent-Pro\backend\winutils\hadoop-3.2.2\bin'

print("Spark Windows 环境变量已设置")
print(f"HADOOP_HOME={os.environ['HADOOP_HOME']}")
