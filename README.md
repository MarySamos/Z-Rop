# 🏦 BankAgent-Pro

> 基于大语言模型的银行数据分析系统
> 数据科学与大数据技术专业 - 毕业设计

## 🎯 项目简介

BankAgent-Pro 是一个智能银行数据分析平台，结合了：
- 🤖 **LangGraph 智能体** - Text-to-SQL + RAG 问答
- 📊 **深度数据分析** - 统计分析、聚类、关联挖掘
- 👥 **用户权限管理** - JWT + RBAC
- 📈 **数据可视化** - Pyecharts + ECharts

## 🛠 技术栈

### 后端
- FastAPI + Uvicorn
- PostgreSQL + pgvector
- LangChain + LangGraph
- Pandas + Scikit-learn

### 前端
- Vue 3 + Vite
- Element Plus
- ECharts

## 📦 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 数据库设置

```bash
# 在 PostgreSQL 中创建数据库
createdb bank_agent

# 启用向量扩展
psql -d bank_agent -c "CREATE EXTENSION vector;"

# 初始化数据库表
python backend/scripts/init_db.py
```

### 3. 配置环境变量

已配置 `.env` 文件，包含：
- OpenAI API Key（阿里云 DashScope）
- 数据库连接信息
- JWT 密钥

### 4. 启动后端

```bash
cd backend
uvicorn main:app --reload
```

访问：http://127.0.0.1:8000/docs

### 5. 启动前端

```bash
cd frontend
npm install
npm run dev
```

访问：http://localhost:5173

## 📂 项目结构

```
BankAgent-Pro/
├── backend/           # 后端代码
│   ├── app/          # 核心应用
│   └── scripts/      # 数据处理脚本
├── frontend/         # 前端代码
├── data/            # 数据和模型
└── notebooks/       # 实验草稿
```

## 🚀 开发进度

- [x] 项目结构创建
- [x] 环境配置文件
- [ ] 数据库表结构
- [ ] 用户认证模块
- [ ] LangGraph 智能体
- [ ] 数据分析模块
- [ ] 前端页面

## 📝 许可证

MIT License
