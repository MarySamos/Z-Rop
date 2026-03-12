"""
Spark 大数据处理服务
从 PostgreSQL 读取真实银行营销数据，进行 Pandas vs Spark 性能对比
"""
import os
import sys
import time
import logging
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 初始化日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============ Windows + Spark 配置 ============
if sys.platform == 'win32':
    # 设置 HADOOP_HOME（自动查找 winutils）
    # __file__ 是 backend/app/services/spark_service.py，需要上移3级到 backend
    backend_dir = Path(__file__).parent.parent.parent
    possible_hadoop_dirs = [
        backend_dir / "winutils" / "hadoop-3.2.2",
        backend_dir / "winutils" / "hadoop-3.3.6",
        backend_dir / "winutils" / "hadoop-3.2.1",
    ]

    for hadoop_dir in possible_hadoop_dirs:
        if hadoop_dir.exists():
            os.environ['HADOOP_HOME'] = str(hadoop_dir)
            hadoop_bin = hadoop_dir / "bin"
            if hadoop_bin.exists():
                os.environ['PATH'] = os.environ.get('PATH', '') + ';' + str(hadoop_bin)
            logger.info(f"Set HADOOP_HOME={hadoop_dir}")
            break
    else:
        logger.warning("Hadoop winutils not found. Spark may not work properly on Windows.")
        logger.warning("Run: python backend/scripts/setup_spark_windows.py")
# ================================================

# 导入 PySpark
try:
    from pyspark.sql import SparkSession
    from pyspark.sql import functions as F
    from pyspark.sql.window import Window
    import pandas as pd
except ImportError as e:
    logging.error(f"PySpark import error: {e}")
    raise


class SparkService:
    """Spark 服务单例类"""
    _spark = None

    # PostgreSQL JDBC 配置
    JDBC_DRIVER = "org.postgresql.Driver"

    @classmethod
    def get_spark(cls):
        """获取单例 SparkSession，包含存活性检查"""
        # 检查 SparkSession 是否存在且仍然活跃
        if cls._spark is not None:
            try:
                # 检查 SparkContext 是否仍然有效
                if cls._spark.sparkContext._jsc is None:
                    logger.warning("SparkSession 已失效，正在重新创建...")
                    cls._spark = None
            except Exception:
                cls._spark = None
        
        if cls._spark is None:
            try:
                # 从环境变量获取数据库配置
                db_user = os.getenv('DATABASE_URL', 'postgresql://postgres:137900@localhost:5432/bank_agent')
                # 解析 DATABASE_URL 格式: postgresql://user:password@host:port/database
                # postgresql://postgres:137900@localhost:5432/bank_agent
                if '@' in db_user:
                    credentials = db_user.split('://')[1].split('@')[0]
                    db_username = credentials.split(':')[0]
                    db_password = credentials.split(':')[1]
                else:
                    db_username = 'postgres'
                    db_password = '137900'

                # 获取 backend 目录的绝对路径
                # __file__ 是 backend/app/services/spark_service.py
                current_file_path = os.path.abspath(__file__)
                # 上移三级: backend/app/services -> backend/app -> backend
                backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_file_path)))
                jdbc_path = os.path.join(backend_dir, 'libs', 'postgresql-42.7.4.jar')

                logger.info(f"Looking for JDBC driver at: {jdbc_path}")

                # 检查 JDBC 驱动是否存在
                if not os.path.exists(jdbc_path):
                    logger.warning(f"JDBC driver not found at {jdbc_path}")
                    logger.warning("Please run: python backend/scripts/download_jdbc_driver.py")

                # local[*] 表示使用所有 CPU 核心
                # Windows specific configurations
                builder = SparkSession.builder \
                    .appName("BankAgentPro-BigDataLAB") \
                    .master("local[*]") \
                    .config("spark.driver.memory", "4g") \
                    .config("spark.ui.showConsoleProgress", "false") \
                    .config("spark.sql.shuffle.partitions", "8") \
                    .config("spark.hadoop.fs.file.impl", "org.apache.hadoop.fs.LocalFileSystem") \
                    .config("spark.sql.warehouse.dir", "spark-warehouse")

                # 在 Windows 上设置 Hadoop 配置
                if sys.platform == 'win32' and 'HADOOP_HOME' in os.environ:
                    hadoop_home = os.environ['HADOOP_HOME']
                    # 将路径转换为正斜杠，避免 Java 中的转义问题
                    hadoop_home_fixed = hadoop_home.replace('\\', '/')
                    # 设置多个 Hadoop 相关配置
                    builder = builder \
                        .config("spark.hadoop.fs.file.impl", "org.apache.hadoop.fs.LocalFileSystem") \
                        .config("spark.executor.extraJavaOptions",
                                f"-Djava.io.tmpdir={os.path.join(backend_dir, 'tmp').replace(chr(92), '/')} -Dhadoop.home.dir={hadoop_home_fixed}") \
                        .config("spark.driver.extraJavaOptions",
                                f"-Dhadoop.home.dir={hadoop_home_fixed}")
                    logger.info(f"Configured Spark with HADOOP_HOME={hadoop_home_fixed}")
                else:
                    builder = builder.config("spark.executor.extraJavaOptions", "-Djava.io.tmpdir=" + os.path.join(backend_dir, "tmp"))

                # 只在 JDBC 驱动存在时添加配置
                if os.path.exists(jdbc_path):
                    builder = builder.config("spark.jars", jdbc_path)
                    logger.info(f"Using JDBC driver: {jdbc_path}")

                cls._spark = builder.getOrCreate()

                logger.info("Spark Session created successfully")
            except Exception as e:
                logger.error(f"Failed to create Spark Session: {e}")
                raise e
        return cls._spark

    @staticmethod
    def get_db_credentials():
        """从环境变量获取数据库凭证和连接信息"""
        db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:137900@localhost:5432/bank_agent')
        # 解析: postgresql://user:password@host:port/database
        if '@' in db_url:
            # 格式: postgresql://user:password@host:port/database
            after_protocol = db_url.split('://')[1]  # user:password@host:port/database
            credentials_part = after_protocol.split('@')[0]  # user:password
            host_part = after_protocol.split('@')[1]  # host:port/database
            
            db_username = credentials_part.split(':')[0]
            db_password = credentials_part.split(':')[1]
            
            host_and_db = host_part.split('/')  # [host:port, database]
            host_port = host_and_db[0]  # host:port
            database = host_and_db[1] if len(host_and_db) > 1 else 'bank_agent'
            
            # 构建 JDBC URL
            jdbc_url = f"jdbc:postgresql://{host_port}/{database}"
        else:
            db_username = 'postgres'
            db_password = '137900'
            jdbc_url = 'jdbc:postgresql://localhost:5432/bank_agent'
        
        return db_username, db_password, jdbc_url
    
    @classmethod
    def stop_spark(cls):
        """安全关闭 SparkSession，释放资源"""
        if cls._spark is not None:
            try:
                cls._spark.stop()
                logger.info("Spark Session 已安全关闭")
            except Exception as e:
                logger.warning(f"关闭 Spark Session 时出错: {e}")
            finally:
                cls._spark = None

    @staticmethod
    def run_benchmark() -> dict:
        """
        运行 Pandas vs Spark 性能基准测试
        使用真实的银行营销数据进行分析

        Returns:
            包含各项测试结果的字典
        """
        results = {
            "data_source": "PostgreSQL - marketing_data 表",
            "tasks": []
        }

        # 从环境变量获取数据库凭证和 JDBC URL
        db_username, db_password, jdbc_url = SparkService.get_db_credentials()

        logger.info("正在从 PostgreSQL 加载银行营销数据...")

        # ========== 1. 加载数据 ==========
        load_start = time.time()

        # Pandas: 使用 SQLAlchemy 读取
        from sqlalchemy import create_engine, text
        engine = create_engine(os.getenv('DATABASE_URL'))

        start_p = time.time()
        pdf = pd.read_sql_query(text("SELECT * FROM marketing_data"), engine)
        pandas_load_time = round(time.time() - start_p, 4)
        results['pandas_load_time'] = pandas_load_time
        logger.info(f"Pandas 加载数据完成: {len(pdf)} 行，耗时 {pandas_load_time}s")

        # Spark: 使用 JDBC 读取
        spark = SparkService.get_spark()
        start_s = time.time()
        sdf = spark.read \
            .format("jdbc") \
            .option("url", jdbc_url) \
            .option("dbtable", "marketing_data") \
            .option("user", db_username) \
            .option("password", db_password) \
            .option("driver", SparkService.JDBC_DRIVER) \
            .load()
        spark_count = sdf.count()
        spark_load_time = round(time.time() - start_s, 4)
        results['spark_load_time'] = spark_load_time
        results['row_count'] = spark_count
        logger.info(f"Spark 加载数据完成: {spark_count} 行，耗时 {spark_load_time}s")

        # 缓存 Spark DataFrame
        sdf.cache()

        # ========== Task 1: 客户群体分析 - 按职业和年龄分组统计 ==========
        logger.info("执行任务 1: 客户群体分析...")

        # Pandas
        start_p = time.time()
        pandas_result_1 = pdf.groupby(['job', pd.cut(pdf['age'], bins=[0, 30, 40, 50, 60, 100])]).agg({
            'balance': 'mean',
            'y': lambda x: (x == 'yes').mean() * 100
        }).round(2)
        time_pandas_1 = round(time.time() - start_p, 4)

        # Spark
        start_s = time.time()
        spark_result_1 = sdf.withColumn('age_group',
            F.when(F.col('age') <= 30, '0-30')
             .when(F.col('age') <= 40, '31-40')
             .when(F.col('age') <= 50, '41-50')
             .when(F.col('age') <= 60, '51-60')
             .otherwise('60+')
        ).groupBy('job', 'age_group').agg(
            F.avg('balance').alias('avg_balance'),
            F.avg(F.when(F.col('y') == 'yes', 1).otherwise(0)).alias('conversion_rate')
        ).collect()
        time_spark_1 = round(time.time() - start_s, 4)

        results['tasks'].append({
            "name": "客户群体分析",
            "description": "按职业和年龄段分组，分析平均余额和转化率",
            "pandas_time": time_pandas_1,
            "spark_time": time_spark_1,
            "speedup": round(time_pandas_1 / time_spark_1, 2) if time_spark_1 > 0 else 0
        })

        # ========== Task 2: 营销转化漏斗分析 - 多条件过滤 + 分组聚合 ==========
        logger.info("执行任务 2: 营销转化漏斗分析...")

        # Pandas
        start_p = time.time()
        pandas_result_2 = pdf[
            (pdf['duration'] > 300) &
            (pdf['previous'] > 0) &
            (pdf['pdays'] != -1)
        ].groupby(['contact', 'month']).agg({
            'y': ['count', lambda x: (x == 'yes').sum()]
        }).round(2)
        time_pandas_2 = round(time.time() - start_p, 4)

        # Spark
        start_s = time.time()
        spark_result_2 = sdf.filter(
            (F.col('duration') > 300) &
            (F.col('previous') > 0) &
            (F.col('pdays') != -1)
        ).groupBy('contact', 'month').agg(
            F.count('*').alias('total_contacts'),
            F.sum(F.when(F.col('y') == 'yes', 1).otherwise(0)).alias('conversions')
        ).collect()
        time_spark_2 = round(time.time() - start_s, 4)

        results['tasks'].append({
            "name": "营销转化漏斗分析",
            "description": "筛选高潜力客户（通话>300秒 且 有历史联系），按联系方式和月份统计转化情况",
            "pandas_time": time_pandas_2,
            "spark_time": time_spark_2,
            "speedup": round(time_pandas_2 / time_spark_2, 2) if time_spark_2 > 0 else 0
        })

        # ========== Task 3: 窗口函数 - 客户价值排名 ==========
        logger.info("执行任务 3: 客户价值排名...")

        # Pandas
        start_p = time.time()
        pdf_temp = pdf.copy()
        pdf_temp['balance_rank'] = pdf_temp.groupby('job')['balance'].rank(ascending=False)
        pdf_temp['duration_rank'] = pdf_temp.groupby('education')['duration'].rank(ascending=False)
        time_pandas_3 = round(time.time() - start_p, 4)

        # Spark
        start_s = time.time()
        window_job = Window.partitionBy('job').orderBy(F.desc('balance'))
        window_edu = Window.partitionBy('education').orderBy(F.desc('duration'))
        sdf_ranked = sdf.withColumn('balance_rank', F.rank().over(window_job)) \
                       .withColumn('duration_rank', F.rank().over(window_edu))
        _ = sdf_ranked.select('id', 'balance_rank', 'duration_rank').limit(100).collect()
        time_spark_3 = round(time.time() - start_s, 4)

        results['tasks'].append({
            "name": "客户价值排名",
            "description": "在各职业内按账户余额排名，在教育程度内按通话时长排名",
            "pandas_time": time_pandas_3,
            "spark_time": time_spark_3,
            "speedup": round(time_pandas_3 / time_spark_3, 2) if time_spark_3 > 0 else 0
        })

        # ========== Task 4: Spark SQL - 复杂营销效果分析 ==========
        logger.info("执行任务 4: 复杂营销效果分析...")

        # 创建临时视图
        sdf.createOrReplaceTempView("marketing")

        # Spark SQL
        start_s = time.time()
        spark_sql_result = spark.sql("""
            SELECT
                poutcome,
                month,
                COUNT(*) as total_contacts,
                SUM(CASE WHEN y = 'yes' THEN 1 ELSE 0 END) as conversions,
                ROUND(AVG(balance), 2) as avg_balance,
                ROUND(AVG(duration), 2) as avg_duration,
                ROUND(SUM(CASE WHEN y = 'yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as conversion_rate
            FROM marketing
            WHERE campaign > 0
            GROUP BY poutcome, month
            HAVING COUNT(*) >= 50
            ORDER BY conversion_rate DESC
            LIMIT 20
        """).collect()
        time_spark_4 = round(time.time() - start_s, 4)

        # Pandas 等效操作
        start_p = time.time()
        filtered = pdf[pdf['campaign'] > 0]
        grouped = filtered.groupby(['poutcome', 'month']).agg({
            'age': 'count',
            'y': [('total', 'count'), ('conversions', lambda x: (x == 'yes').sum())],
            'balance': 'mean',
            'duration': 'mean'
        })
        grouped.columns = ['_'.join(col).strip() for col in grouped.columns.values]
        grouped['conversion_rate'] = (grouped['y_conversions'] / grouped['age_count'] * 100).round(2)
        pandas_result_4 = grouped[grouped['age_count'] >= 50].sort_values('conversion_rate', ascending=False).head(20)
        time_pandas_4 = round(time.time() - start_p, 4)

        results['tasks'].append({
            "name": "复杂营销效果分析",
            "description": "按上一次营销结果和月份分析转化率，筛选至少50次联系的组合",
            "pandas_time": time_pandas_4,
            "spark_time": time_spark_4,
            "speedup": round(time_pandas_4 / time_spark_4, 2) if time_spark_4 > 0 else 0
        })

        # ========== Task 5: 自连接查询 - 客户行为模式分析 ==========
        logger.info("执行任务 5: 客户行为模式分析...")

        # Spark: 优化的聚合后 join（避免笛卡尔积）
        start_s = time.time()
        converted_stats = sdf.filter(F.col('y') == 'yes').groupBy('job', 'education').agg(
            F.countDistinct('id').alias('converted_customers'),
            F.avg('balance').alias('converted_avg_balance')
        )
        not_converted_stats = sdf.filter(F.col('y') == 'no').groupBy('job', 'education').agg(
            F.countDistinct('id').alias('not_converted_customers'),
            F.avg('balance').alias('not_converted_avg_balance')
        )
        spark_result_5 = converted_stats.join(
            not_converted_stats, 
            ['job', 'education'], 
            'full_outer'
        ).collect()
        time_spark_5 = round(time.time() - start_s, 4)

        # Pandas: 使用同样的聚合后 merge 逻辑
        start_p = time.time()
        converted = pdf[pdf['y'] == 'yes'].groupby(['job', 'education']).agg(
            converted_customers=('id', 'nunique'),
            converted_avg_balance=('balance', 'mean')
        ).reset_index()
        not_converted = pdf[pdf['y'] == 'no'].groupby(['job', 'education']).agg(
            not_converted_customers=('id', 'nunique'),
            not_converted_avg_balance=('balance', 'mean')
        ).reset_index()
        pandas_result_5 = converted.merge(not_converted, on=['job', 'education'], how='outer')
        time_pandas_5 = round(time.time() - start_p, 4)

        results['tasks'].append({
            "name": "客户行为模式分析",
            "description": "对比同职业同教育程度下，转化客户与未转化客户的余额差异",
            "pandas_time": time_pandas_5,
            "spark_time": time_spark_5,
            "speedup": round(time_pandas_5 / time_spark_5, 2) if time_spark_5 > 0 else 0
        })

        # 计算总耗时（不包括数据加载）
        results['total_pandas'] = round(sum(t['pandas_time'] for t in results['tasks']), 4)
        results['total_spark'] = round(sum(t['spark_time'] for t in results['tasks']), 4)
        results['overall_speedup'] = round(results['total_pandas'] / results['total_spark'], 2) if results['total_spark'] > 0 else 0

        logger.info(f"基准测试完成: Pandas={results['total_pandas']}s, Spark={results['total_spark']}s")

        # 清理缓存，释放内存
        sdf.unpersist()
        logger.info("DataFrame 缓存已清理")

        return results


# 模块级单例
spark_service = SparkService()
