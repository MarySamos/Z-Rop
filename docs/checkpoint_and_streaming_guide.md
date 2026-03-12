# Checkpoint 和流式输出使用指南

本文档说明如何使用新增的 **Checkpoint 会话记忆** 和 **流式输出** 功能。

---

## 📚 功能概述

### 1️⃣ Checkpoint（会话记忆持久化）

LangGraph 的 Checkpoint 功能允许：
- ✅ 保存和恢复对话状态
- ✅ 支持长时间记忆（跨请求）
- ✅ 多用户多会话隔离
- ✅ 持久化存储（内存或 PostgreSQL）

### 2️⃣ 流式输出（Streaming）

实时返回工作流执行过程：
- ✅ 逐节点返回执行结果
- ✅ 实时查看意图识别、SQL生成、查询执行等
- ✅ 更好的用户体验
- ✅ 使用 Server-Sent Events (SSE) 实现

---

## 🚀 快速开始

### 安装依赖

```bash
cd backend
pip install -r ../requirements.txt
```

### 配置（可选）

在 `.env` 文件中添加 Checkpoint 配置：

```bash
# Checkpoint 类型：memory（内存）或 postgres（PostgreSQL）
CHECKPOINT_TYPE=memory

# 如果使用 PostgreSQL 存储
CHECKPOINT_DB_URL=postgresql://user:password@localhost:5432/bankagent
```

默认使用内存存储，无需额外配置。

---

## 📡 API 端点

### 1. 普通聊天（支持会话记忆）

**端点**: `POST /api/v1/chat/send`

**请求示例**:
```json
{
    "message": "查询余额大于5000的客户",
    "session_id": "user123_session456",
    "user_id": "user123"
}
```

**响应示例**:
```json
{
    "answer": "查询到 42 个余额大于 5000 的客户...",
    "chart": null,
    "sql": "SELECT * FROM marketing_data WHERE balance > 5000",
    "intent": "query",
    "session_id": "user123_session456"
}
```

**特性**:
- 自动保存对话状态到 checkpoint
- 相同 `session_id` 的对话会保持上下文记忆
- 支持多轮对话

### 2. 流式聊天（实时输出）

**端点**: `POST /api/v1/chat/stream`

**请求示例**:
```json
{
    "message": "分析一下客户年龄分布",
    "session_id": "user123_session456",
    "user_id": "user123"
}
```

**响应格式（Server-Sent Events）**:
```
data: {"type": "intent", "content": {"intent": "stats"}}

data: {"type": "analysis", "content": {"stats": {...}}}

data: {"type": "final_answer", "content": {"answer": "..."}}

data: {"type": "done", "content": {"status": "stream_ended"}}
```

**事件类型**:
- `intent`: 意图识别结果
- `sql`: 生成的 SQL 语句
- `query_result`: SQL 执行结果摘要
- `analysis`: 统计分析结果
- `visualization`: 可视化图表
- `final_answer`: 最终回答
- `error`: 错误信息
- `done`: 流结束

### 3. 清除会话记忆

**端点**: `DELETE /api/v1/chat/session/{session_id}`

**示例**:
```bash
curl -X DELETE http://localhost:8000/api/v1/chat/session/user123_session456
```

**响应**:
```json
{
    "status": "success",
    "message": "会话 user123_session456 已清除"
}
```

---

## 💡 使用示例

### Python 客户端（普通聊天）

```python
import requests

API_URL = "http://localhost:8000/api/v1/chat/send"
session_id = "my_session_123"

# 第一轮对话
response1 = requests.post(API_URL, json={
    "message": "查询年龄大于30的客户",
    "session_id": session_id,
    "user_id": "user123"
})
print(response1.json())

# 第二轮对话（会记住上一轮的上下文）
response2 = requests.post(API_URL, json={
    "message": "他们当中有多少人买了房？",
    "session_id": session_id,
    "user_id": "user123"
})
print(response2.json())
```

### Python 客户端（流式聊天）

```python
import requests
import json

API_URL = "http://localhost:8000/api/v1/chat/stream"

response = requests.post(
    API_URL,
    json={
        "message": "分析职业分布情况",
        "session_id": "my_session_123",
        "user_id": "user123"
    },
    stream=True
)

# 读取流式响应
for line in response.iter_lines():
    if line:
        line = line.decode('utf-8')
        if line.startswith('data: '):
            data = json.loads(line[6:])  # 去掉 'data: ' 前缀
            print(f"[{data['type']}] {data['content']}")
```

**输出示例**:
```
[intent] {'intent': 'stats'}
[analysis] {'stats': {'row_count': 45211, ...}}
[final_answer] {'answer': '职业分布情况如下...'}
[done] {'status': 'stream_ended'}
```

### JavaScript 客户端（流式聊天）

```javascript
const API_URL = 'http://localhost:8000/api/v1/chat/stream';

const eventSource = new EventSource(
    `${API_URL}?` + new URLSearchParams({
        message: '生成客户余额分布图',
        session_id: 'my_session_123',
        user_id: 'user123'
    })
);

// 注意：EventSource 只支持 GET，实际需要使用 fetch + stream

// 推荐使用 fetch:
async function streamChat(message, sessionId) {
    const response = await fetch('http://localhost:8000/api/v1/chat/stream', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            message: message,
            session_id: sessionId,
            user_id: 'user123'
        })
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
        const {done, value} = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
            if (line.startsWith('data: ')) {
                const data = JSON.parse(line.substring(6));
                console.log(`[${data.type}]`, data.content);
            }
        }
    }
}

// 使用示例
streamChat('查询余额最高的客户', 'session_123');
```

---

## 🗄️ PostgreSQL Checkpoint 配置（可选）

如果需要持久化会话记忆（服务器重启后仍保留），配置 PostgreSQL Checkpoint：

### 1. 创建专用数据库

```sql
CREATE DATABASE bankagent_checkpoint;
```

### 2. 更新 .env 配置

```bash
CHECKPOINT_TYPE=postgres
CHECKPOINT_DB_URL=postgresql://postgres:password@localhost:5432/bankagent_checkpoint
```

### 3. 启动服务

```bash
cd backend
python -m uvicorn main:app --reload
```

服务会自动创建必要的表结构。

---

## ⚙️ 配置选项

### 内存存储（默认）
```bash
CHECKPOINT_TYPE=memory
```
- ✅ 无需配置
- ❌ 服务重启后数据丢失
- 💡 适合开发环境

### PostgreSQL 持久化
```bash
CHECKPOINT_TYPE=postgres
CHECKPOINT_DB_URL=postgresql://user:pass@host:port/db
```
- ✅ 数据持久化
- ✅ 支持分布式部署
- 💡 适合生产环境

---

## 🔍 工作流说明

### Checkpoint 工作原理

```
用户请求 (session_id: "user123")
    ↓
LangGraph 检查 checkpoint
    ↓
恢复之前的会话状态（如果有）
    ↓
执行工作流节点
    ├─ 意图识别
    ├─ SQL 生成
    ├─ 执行查询
    └─ 生成回答
    ↓
保存新状态到 checkpoint
    ↓
返回结果
```

### 流式输出工作原理

```
用户请求
    ↓
开始流式执行工作流
    ↓
每个节点执行完立即返回结果
    ├─ [intent] 意图识别完成
    ├─ [sql] SQL 生成完成
    ├─ [query_result] 查询执行完成
    └─ [final_answer] 回答生成完成
    ↓
[done] 流结束
```

---

## 📝 最佳实践

### 1. Session ID 管理

- 使用唯一标识符：`{user_id}_{timestamp}` 或 UUID
- 每个用户/设备使用独立的 session_id
- 定期清理过期会话

```python
import uuid

# 生成新会话
session_id = f"{user_id}_{uuid.uuid4()}"

# 或使用时间戳
import time
session_id = f"{user_id}_{int(time.time())}"
```

### 2. 错误处理

```python
try:
    response = requests.post(API_URL, json={...})
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    print(f"请求失败: {e}")
```

### 3. 流式响应超时

```python
response = requests.post(API_URL, json={...}, stream=True, timeout=30)
```

### 4. 会话清理

定期清理过期会话：

```python
# 清除指定会话
requests.delete(f"{API_URL}/session/{session_id}")
```

---

## 🐛 故障排除

### 问题 1: Checkpoint 初始化失败

**错误**: `PostgreSQL Checkpoint 初始化失败`

**解决**:
1. 检查数据库连接字符串是否正确
2. 确保数据库存在
3. 回退到内存存储：`CHECKPOINT_TYPE=memory`

### 问题 2: 流式响应中断

**错误**: SSE 连接意外断开

**解决**:
1. 检查 Nginx/代理配置（禁用缓冲）
2. 增加超时时间
3. 检查服务端日志

### 问题 3: 会话记忆不生效

**检查**:
1. 确保每次请求使用相同的 `session_id`
2. 查看 checkpoint 配置是否正确
3. 检查服务端日志

---

## 📚 相关文档

- [LangGraph 官方文档 - Checkpoints](https://langchain-ai.github.io/langgraph/concepts/persistence/)
- [LangGraph 官方文档 - Streaming](https://langchain-ai.github.io/langgraph/concepts/low_level/#streaming)
- [Server-Sent Events (SSE) 规范](https://html.spec.whatwg.org/multipage/server-sent-events.html)

---

## 🎯 下一步

1. ✅ 基础功能已实现
2. 🔜 添加前端集成示例
3. 🔜 实现会话管理界面
4. 🔜 添加性能监控和日志

---

**最后更新**: 2026-01-09
