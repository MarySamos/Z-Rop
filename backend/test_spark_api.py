"""
测试 Spark API 对接
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.services.spark_service import spark_service
import json

print("=" * 80)
print("Spark API 测试")
print("=" * 80)
print()

# 测试 1: 检查 Spark 状态
print("1. 检查 Spark 状态...")
try:
    spark = spark_service.get_spark()
    status = {
        "status": "running",
        "app_name": spark.sparkContext.appName,
        "master": spark.sparkContext.master,
        "version": spark.version,
        "cores": spark.sparkContext.defaultParallelism
    }
    print(f"   Status: {status['status']}")
    print(f"   App Name: {status['app_name']}")
    print(f"   Master: {status['master']}")
    print(f"   Version: {status['version']}")
    print(f"   Cores: {status['cores']}")
    print()
except Exception as e:
    print(f"   Error: {e}")
    print()
    status = {"status": "error", "message": str(e)}

# 测试 2: 运行基准测试
print("2. 运行基准测试...")
try:
    result = spark_service.run_benchmark()
    print(f"   数据源: {result['data_source']}")
    print(f"   数据行数: {result['row_count']:,}")
    print(f"   Pandas 加载时间: {result['pandas_load_time']}s")
    print(f"   Spark 加载时间: {result['spark_load_time']}s")
    print(f"   Pandas 总耗时: {result['total_pandas']}s")
    print(f"   Spark 总耗时: {result['total_spark']}s")
    print(f"   加速比: {result['overall_speedup']}x")
    print()
    print("   各任务结果:")
    for i, task in enumerate(result['tasks'], 1):
        print(f"   {i}. {task['name']}")
        print(f"      Pandas: {task['pandas_time']}s, Spark: {task['spark_time']}s, 加速比: {task['speedup']}x")
    print()

    # 保存结果到 JSON 文件
    output_file = os.path.join(os.path.dirname(__file__), 'logs', 'spark_api_test_result.json')
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"   结果已保存到: {output_file}")

except Exception as e:
    print(f"   Error: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 80)
print("测试完成")
print("=" * 80)
print()

# 输出 API 响应示例（用于前端对接验证）
print("API 响应示例（前端应该接收到这样的数据）：")
print()
print(json.dumps({
    "status": status,
    "result": result if 'result' in locals() else None
}, ensure_ascii=False, indent=2))
