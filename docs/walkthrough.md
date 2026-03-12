# BankAgent-Pro Backend 代码审查报告

## 📋 审查范围

对 `backend` 目录下的核心模块进行了全面代码审查：

| 模块 | 文件 | 状态 |
|------|------|------|
| graphs | [workflow.py](file:///g:/PycharmProjects/BankAgent-Pro/backend/app/graphs/workflow.py), [nodes.py](file:///g:/PycharmProjects/BankAgent-Pro/backend/app/graphs/nodes.py), [state.py](file:///g:/PycharmProjects/BankAgent-Pro/backend/app/graphs/state.py), [tools.py](file:///g:/PycharmProjects/BankAgent-Pro/backend/app/graphs/tools.py), [checkpoint_manager.py](file:///g:/PycharmProjects/BankAgent-Pro/backend/app/graphs/checkpoint_manager.py) | ✅ 已审查 |
| api | [api_v1.py](file:///g:/PycharmProjects/BankAgent-Pro/backend/app/api/api_v1.py), [dependencies.py](file:///g:/PycharmProjects/BankAgent-Pro/backend/app/api/dependencies.py) | ✅ 已审查 |
| endpoints | [chat.py](file:///g:/PycharmProjects/BankAgent-Pro/backend/app/schemas/chat.py), [chat_stream.py](file:///g:/PycharmProjects/BankAgent-Pro/backend/app/api/endpoints/chat_stream.py) | ✅ 已审查 |
| core | [config.py](file:///g:/PycharmProjects/BankAgent-Pro/backend/spark_config.py), [database.py](file:///g:/PycharmProjects/BankAgent-Pro/backend/app/core/database.py) | ✅ 已审查 |
| db | [models.py](file:///g:/PycharmProjects/BankAgent-Pro/backend/app/db/models.py) | ✅ 已审查 |

---

## 🚨 高优先级问题

### 1. SQL 注入风险

> [!CAUTION]
> 多处使用字符串拼接构建 SQL 查询

**文件**: [tools.py](file:///g:/PycharmProjects/BankAgent-Pro/backend/app/graphs/tools.py)

```python
# 第 139-144 行 - 使用 f-string 拼接 SQL
result = conn.execute(text(f"""
    SELECT column_name, data_type, is_nullable
    FROM information_schema.columns
    WHERE table_name = '{table_name}'  # ❌ 危险！
    ORDER BY ordinal_position
"""))
```

**同样存在问题的位置**：
- 第 159 行: `f"SELECT COUNT(*) FROM {table_name}"`
- 第 180 行: `f"SELECT * FROM {table_name} LIMIT {limit}"`
- 第 201 行: `pd.read_sql(f"SELECT * FROM {table_name}", engine)`
- 第 251-257 行: [get_column_distribution](file:///g:/PycharmProjects/BankAgent-Pro/backend/app/graphs/tools.py#237-269) 函数
- 第 287-296 行: [get_conversion_rate](file:///g:/PycharmProjects/BankAgent-Pro/backend/app/graphs/tools.py#271-307) 函数

**建议修复**：使用参数化查询或白名单验证

```python
# 方法1: 白名单验证
ALLOWED_TABLES = {"marketing_data", "users", "knowledge_docs"}
if table_name not in ALLOWED_TABLES:
    raise ValueError(f"不允许访问表: {table_name}")

# 方法2: 使用 SQLAlchemy 的参数化
from sqlalchemy import bindparam
```

---

### 2. 数据库连接池重复创建

> [!WARNING]
> 存在两个独立的数据库引擎实例

**文件 1**: [tools.py](file:///g:/PycharmProjects/BankAgent-Pro/backend/app/graphs/tools.py#L19-39)
```python
_db_engine = None

def get_db_engine():
    global _db_engine
    if _db_engine is None:
        _db_engine = create_engine(settings.DATABASE_URL, ...)
```

**文件 2**: [database.py](file:///g:/PycharmProjects/BankAgent-Pro/backend/app/core/database.py#L17-23)
```python
engine = create_engine(settings.DATABASE_URL, ...)
```

**问题**: 两个模块各自创建了连接池，浪费资源且可能导致连接数超限。

**建议**: 统一使用 [core/database.py](file:///g:/PycharmProjects/BankAgent-Pro/backend/app/core/database.py) 中的 [engine](file:///g:/PycharmProjects/BankAgent-Pro/backend/app/graphs/tools.py#19-40)，删除 [tools.py](file:///g:/PycharmProjects/BankAgent-Pro/backend/app/graphs/tools.py) 中的重复实现。

---

### 3. LLM 单例模式问题

> [!WARNING]
> LLMManager 的单例实现可能导致 temperature 参数配置不生效

**文件**: [nodes.py](file:///g:/PycharmProjects/BankAgent-Pro/backend/app/graphs/nodes.py#L22-45)

```python
class LLMManager:
    _instance = None

    @classmethod
    def get_llm(cls, temperature: float = 0.1) -> ChatOpenAI:
        if cls._instance is None:  # 首次调用后，temperature 参数被忽略
            cls._instance = ChatOpenAI(...)
        return cls._instance
```

**问题**: 一旦实例创建，后续调用 [get_llm(temperature=0.5)](file:///g:/PycharmProjects/BankAgent-Pro/backend/app/graphs/nodes.py#27-46) 时参数会被忽略。

**建议**:
- 移除 `temperature` 参数，在 [__init__](file:///g:/PycharmProjects/BankAgent-Pro/backend/app/services/analysis_service.py#19-21) 中固定
- 或改为缓存不同 temperature 的实例

---

## ⚠️ 中等优先级问题

### 4. 异常处理过于宽泛

**文件**: [nodes.py](file:///g:/PycharmProjects/BankAgent-Pro/backend/app/graphs/nodes.py#L62-68)

```python
def wrapper(state: AgentState) -> dict:
    try:
        return func(state)
    except Exception as e:  # ❌ 捕获所有异常，难以调试
        error_msg = f"{node_name}: {str(e)}"
        print(f"[ERROR] {error_msg}")  # ❌ 使用 print 而非 logging
        return {"error_message": error_msg}
```

**建议**:
1. 使用 `logging` 模块替代 `print`
2. 区分可恢复和不可恢复的异常
3. 记录完整的 traceback

---

### 5. [execute_query](file:///g:/PycharmProjects/BankAgent-Pro/backend/app/graphs/nodes.py#144-161) 节点未处理 [execute_sql](file:///g:/PycharmProjects/BankAgent-Pro/backend/app/graphs/tools.py#44-122) 返回值

**文件**: [nodes.py](file:///g:/PycharmProjects/BankAgent-Pro/backend/app/graphs/nodes.py#L144-160)

```python
def execute_query(state: AgentState) -> dict:
    sql = state.get("generated_sql", "")
    if not sql:
        raise ValueError("No SQL to execute")

    result = execute_sql(sql)  # 返回 Dict 包含 success, data, error

    print(f"[INFO] Query executed, returned {len(result)} rows")  # ❌ result 是 Dict，不是 List
    return {"sql_result": result}  # ❌ 应该是 result["data"]
```

**问题**: 
- [execute_sql](file:///g:/PycharmProjects/BankAgent-Pro/backend/app/graphs/tools.py#44-122) 返回 `Dict`，但代码假设它是 `List`
- 未检查 `result["success"]`
- `len(result)` 实际是字典的 key 数量，而不是行数

**建议修复**：
```python
result = execute_sql(sql)
if not result["success"]:
    return {"sql_error": result["error"]}
print(f"[INFO] Query executed, returned {result['row_count']} rows")
return {"sql_result": result["data"]}
```

---

### 6. 硬编码的 LLM 配置

**文件**: [nodes.py](file:///g:/PycharmProjects/BankAgent-Pro/backend/app/graphs/nodes.py#L39-44)

```python
cls._instance = ChatOpenAI(
    model="glm-4",  # ❌ 硬编码模型名
    temperature=temperature,
    openai_api_key=settings.ZHIPU_API_KEY,
    openai_api_base="https://open.bigmodel.cn/api/paas/v4/"  # ❌ 硬编码 URL
)
```

**建议**: 移动到 [config.py](file:///g:/PycharmProjects/BankAgent-Pro/backend/spark_config.py) 中配置

```python
# config.py
LLM_MODEL: str = "glm-4"
LLM_API_BASE: Optional[str] = "https://open.bigmodel.cn/api/paas/v4/"
```

---

### 7. 废弃的 `declarative_base`

**文件**: [database.py](file:///g:/PycharmProjects/BankAgent-Pro/backend/app/core/database.py#L7)

```python
from sqlalchemy.ext.declarative import declarative_base  # ❌ 已废弃

Base = declarative_base()
```

**建议**: 使用新的导入方式

```python
from sqlalchemy.orm import declarative_base  # ✅ 新版本
# 或者
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass
```

---

## 💡 低优先级建议

### 8. 代码风格优化

- **缺少类型注解**: [services/analysis_service.py](file:///g:/PycharmProjects/BankAgent-Pro/backend/app/services/analysis_service.py) 中部分方法缺少返回类型

- **日志不一致**: 混用 `print()` 和 `logging`

- **魔法字符串**: 意图类型 ("query", "stats", "viz", "chat") 建议改为 Enum

```python
from enum import Enum

class Intent(str, Enum):
    QUERY = "query"
    STATS = "stats"
    VIZ = "viz"
    CHAT = "chat"
```

---

### 9. 安全建议

- **CORS 配置**: 生产环境 `allowed_origins` 为空列表，需要配置实际域名

- **JWT Secret**: 确保 `SECRET_KEY` 使用足够强度的随机值

---

## 📊 问题统计

| 严重程度 | 数量 | 需修复 |
|----------|------|--------|
| 🔴 高 | 3 | ✅ 建议立即修复 |
| 🟡 中 | 4 | ⚡ 建议尽快修复 |
| 🟢 低 | 2 | 📝 可选优化 |

---

## ✅ 代码亮点

1. **良好的模块化**: `graphs/` 模块分离清晰（State, Nodes, Tools, Workflow）
2. **Checkpoint 支持**: 实现了会话记忆持久化
3. **安全措施**: SQL 执行限制只允许 SELECT，禁止危险关键字
4. **文档完善**: 大部分函数有 docstring
5. **流式输出**: 支持 SSE 流式响应
