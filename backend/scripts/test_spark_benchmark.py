"""
测试 Spark 基准测试脚本
"""
import sys
import os

# 添加 backend 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.spark_service import spark_service
import json


def test_spark():
    print("=" * 80)
    print("Spark vs Pandas 性能基准测试")
    print("=" * 80)
    print()

    try:
        print("1. 初始化 Spark...")
        spark = spark_service.get_spark()
        print(f"   Spark version: {spark.version}")
        print(f"   Master: {spark.sparkContext.master}")
        print(f"   App Name: {spark.sparkContext.appName}")
        print()

        print("2. 开始基准测试...")
        print("   这将执行以下任务：")
        print("   - 客户群体分析")
        print("   - 营销转化漏斗分析")
        print("   - 客户价值排名")
        print("   - 复杂营销效果分析")
        print("   - 客户行为模式分析")
        print()

        results = spark_service.run_benchmark()

        print()
        print("=" * 80)
        print("测试结果")
        print("=" * 80)
        print()

        print(f"数据源: {results['data_source']}")
        print(f"数据行数: {results['row_count']:,}")
        print()
        print(f"数据加载时间:")
        print(f"  - Pandas: {results['pandas_load_time']:.4f}s")
        print(f"  - Spark:  {results['spark_load_time']:.4f}s")
        print()
        print(f"各任务性能对比:")
        print("-" * 80)
        print(f"{'任务名称':<30} {'Pandas(s)':<12} {'Spark(s)':<12} {'加速比':<10}")
        print("-" * 80)

        for task in results['tasks']:
            print(f"{task['name']:<30} {task['pandas_time']:<12.4f} {task['spark_time']:<12.4f} {task['speedup']:<10.2f}x")

        print("-" * 80)
        print(f"{'总计':<30} {results['total_pandas']:<12.4f} {results['total_spark']:<12.4f} {results['overall_speedup']:<10.2f}x")
        print()

        if results['overall_speedup'] > 1:
            print(f"Spark 比 Pandas 快 {results['overall_speedup']:.2f} 倍")
        elif results['overall_speedup'] < 1:
            print(f"Pandas 比 Spark 快 {1/results['overall_speedup']:.2f} 倍")
        else:
            print("Spark 和 Pandas 性能相当")

        print()
        print("=" * 80)
        print("测试完成!")
        print("=" * 80)

        # 保存结果到 JSON 文件
        output_file = os.path.join(os.path.dirname(__file__), '..', 'logs', 'spark_benchmark_results.json')
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"详细结果已保存到: {output_file}")

    except Exception as e:
        print()
        print("=" * 80)
        print("测试失败")
        print("=" * 80)
        print(f"错误信息: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = test_spark()
    sys.exit(exit_code)
