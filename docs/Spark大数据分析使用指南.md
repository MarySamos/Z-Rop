# Spark 大数据分析功能使用指南

## 📖 功能概述

Spark 大数据分析功能通过对比 **Pandas** 和 **Apache Spark** 在真实银行营销数据处理上的性能差异，展示大数据技术的优势。

### 核心特性

- ✅ **真实数据**：直接从 PostgreSQL 读取银行营销数据
- ✅ **5个测试场景**：涵盖常见的银行业务分析场景
- ✅ **性能对比**：直观展示 Pandas vs Spark 的性能差异
- ✅ **实用性强**：所有测试基于真实的营销数据分析需求

---

## 🚀 快速开始

### 1. 环境准备

#### 1.1 Java 环境
Spark 需要 Java 运行环境，确保已安装以下任一版本：
- JDK 8
- JDK 11
- JDK 17
- JDK 21

检查 Java 是否安装：
```bash
java -version
```

#### 1.2 Python 依赖
安装必要的 Python 包：
```bash
pip install pyspark findspark
```

#### 1.3 PostgreSQL 数据库
确保 PostgreSQL 正在运行，并已导入银行营销数据：
```bash
# 检查数据库连接
psql -U postgres -d bank_agent -c "SELECT COUNT(*) FROM marketing_data;"
```

### 2. 下载 JDBC 驱动

使用提供的脚本自动下载 PostgreSQL JDBC 驱动：

```bash
cd backend
python scripts/download_jdbc_driver.py
```

**手动下载（备选方案）**：
1. 访问：https://jdbc.postgresql.org/download/postgresql-42.7.4.jar
2. 将下载的文件保存到：`backend/libs/postgresql-42.7.4.jar`

### 3. 启动服务

```bash
cd backend
python -m uvicorn app.main:app --reload
```

### 4. 访问 API

打开浏览器访问：http://localhost:8000/docs

找到 **BigData** 分组，调用以下接口：

#### POST /api/bigdata/benchmark
执行基准测试，返回性能对比结果

#### GET /api/bigdata/status
检查 Spark 环境状态

---

## 📊 测试场景说明

### Task 1: 客户群体分析
**目的**：按职业和年龄段分析客户特征

**分析维度**：
- 按职业（job）和年龄段分组
- 计算平均账户余额
- 计算转化率（订阅定期存款的比例）

**业务价值**：
- 识别高价值客户群体
- 为精准营销提供数据支持

### Task 2: 营销转化漏斗分析
**目的**：筛选高潜力客户并分析转化情况

**筛选条件**：
- 通话时长 > 300秒
- 有历史营销记录（previous > 0）
- 距离上次联系天数 != -1（表示有过联系）

**分析维度**：
- 按联系方式（contact）和月份（month）分组
- 统计总联系数和转化数

**业务价值**：
- 识别营销活动的最佳时机
- 优化联系方式选择

### Task 3: 客户价值排名
**目的**：使用窗口函数进行客户价值排名

**排名规则**：
- 在各职业内按账户余额排名
- 在教育程度内按通话时长排名

**技术亮点**：
- 使用 Spark 窗口函数
- 对比 Pandas rank() 方法

**业务价值**：
- 识别各群体中的头部客户
- 优先服务高价值客户

### Task 4: 复杂营销效果分析
**目的**：多维度分析营销活动效果

**分析维度**：
- 按上次营销结果（poutcome）和月份（month）分组
- 计算总联系数、转化数、平均余额、平均通话时长
- 计算转化率

**筛选条件**：
- 只分析至少 50 次联系的组合（确保统计意义）
- 只分析有营销活动的记录（campaign > 0）

**业务价值**：
- 评估不同营销策略的效果
- 优化营销资源配置

### Task 5: 客户行为模式分析
**目的**：对比转化客户与未转化客户的差异

**分析方法**：
- 自连接查询
- 对比相同职业和教育程度的两类客户

**对比指标**：
- 转化客户数量 vs 未转化客户数量
- 平均账户余额差异

**业务价值**：
- 理解客户转化的关键因素
- 优化客户筛选标准

---

## 📈 返回结果说明

API 返回的 JSON 包含以下字段：

```json
{
  "data_source": "PostgreSQL - marketing_data 表",
  "row_count": 41188,
  "pandas_load_time": 0.5234,
  "spark_load_time": 0.8123,
  "tasks": [
    {
      "name": "客户群体分析",
      "description": "按职业和年龄段分组，分析平均余额和转化率",
      "pandas_time": 0.1234,
      "spark_time": 0.0567,
      "speedup": 2.18
    }
  ],
  "total_pandas": 1.2345,
  "total_spark": 0.4567,
  "overall_speedup": 2.70
}
```

### 字段说明

| 字段 | 说明 |
|------|------|
| `data_source` | 数据来源说明 |
| `row_count` | 数据行数 |
| `pandas_load_time` | Pandas 从数据库加载数据的耗时（秒） |
| `spark_load_time` | Spark 从数据库加载数据的耗时（秒） |
| `tasks` | 各项任务的测试结果数组 |
| `total_pandas` | Pandas 总耗时（不含数据加载，秒） |
| `total_spark` | Spark 总耗时（不含数据加载，秒） |
| `overall_speedup` | Spark 相对于 Pandas 的加速比 |

### 性能解读

- **speedup > 1**：Spark 更快（数值越大，加速越明显）
- **speedup = 1**：两者性能相当
- **speedup < 1**：Pandas 更快
- **数据量越大，Spark 优势越明显**

---

## 🔧 常见问题排查

### 问题 1: Spark 启动失败 - Java 环境

**错误信息**：
```
Spark 启动失败：未检测到 Java 环境
```

**解决方案**：
1. 检查 Java 是否安装：`java -version`
2. 安装 JDK：推荐 OpenJDK 11 或 17
3. 设置 JAVA_HOME 环境变量

### 问题 2: PySpark 模块未安装

**错误信息**：
```
PySpark 模块未安装
```

**解决方案**：
```bash
pip install pyspark findspark
```

### 问题 3: 数据库连接失败

**错误信息**：
```
数据库连接失败：请确保 PostgreSQL 正在运行
```

**解决方案**：
1. 检查 PostgreSQL 服务是否运行
2. 验证数据库连接信息（.env 文件中的 DATABASE_URL）
3. 确保 JDBC 驱动已下载到 `backend/libs/` 目录

### 问题 4: 数据表不存在

**错误信息**：
```
数据表不存在：请确保已导入银行营销数据
```

**解决方案**：
1. 检查数据库是否有数据：
   ```bash
   psql -U postgres -d bank_agent -c "\dt"
   ```
2. 如果没有数据，运行数据导入脚本：
   ```bash
   cd backend/scripts
   python import_csv.py
   ```

### 问题 5: 内存不足

**错误信息**：
```
Java heap space
```

**解决方案**：
修改 `spark_service.py` 中的内存配置：
```python
.config("spark.driver.memory", "4g")  # 增加到 8g
```

---

## 💡 使用建议

### 何时使用 Spark？

**推荐使用 Spark 的场景**：
- ✅ 数据量 > 100万行
- ✅ 需要复杂的多表关联
- ✅ 需要分布式计算
- ✅ 需要实时流处理
- ✅ 内存不足以加载全部数据

**推荐使用 Pandas 的场景**：
- ✅ 数据量 < 50万行
- ✅ 简单的数据处理
- ✅ 快速原型开发
- ✅ 单机环境

### 性能优化建议

1. **数据缓存**：对于多次使用的数据，使用 `cache()` 方法
2. **分区优化**：根据数据量调整 `spark.sql.shuffle.partitions`
3. **内存配置**：根据机器配置调整 `spark.driver.memory`
4. **并行度**：利用多核 CPU，使用 `local[*]`

---

## 📚 技术栈

- **Apache Spark**: 3.x（分布式计算引擎）
- **PySpark**: Python API for Spark
- **PostgreSQL**: 关系型数据库
- **JDBC**: 数据库连接驱动
- **Pandas**: Python 数据分析库
- **SQLAlchemy**: Python SQL 工具包

---

## 🎯 后续优化方向

- [ ] 支持更多数据源（CSV、Parquet、Hive）
- [ ] 添加更多测试场景（机器学习、图计算）
- [ ] 可视化性能对比结果
- [ ] 支持 Spark Standalone 集群模式
- [ ] 添加实时数据流处理示例

---

## 📞 技术支持

如有问题，请查阅：
- 项目文档：`docs/` 目录
- API 文档：http://localhost:8000/docs
- 日志文件：`backend/logs/app.log`

---

**最后更新**：2026-01-08
**版本**：v1.0.0
