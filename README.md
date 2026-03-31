# 🏦 Z-Rop

> 基于大语言模型的智能银行数据分析与客服系统
>
> 数据科学与大数据技术专业 - 毕业设计

[![Vue](https://img.shields.io/badge/Vue-3.4-42b883?logo=vue.js)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![LangChain](https://img.shields.io/badge/LangChain-Latest-1CA854?logo=langchain)](https://langchain.com/)

---

## 🎯 项目简介

Z-Rop是一个智能银行数据分析与客服平台，融合了：

- 🤖 **LangGraph 智能体** - Text-to-SQL 自然语言查询 + RAG 知识库问答
- 📊 **深度数据分析** - 统计分析、K-means 聚类、关联规则挖掘、漏斗分析
- 📈 **预测建模** - PCA 降维、机器学习预测、时序分析
- 👥 **用户权限管理** - JWT 认证 + RBAC 角色权限
- 🎨 **极简 UI 设计** - 淡米白纸感主题，类 macOS Dock 导航体验

---

## 🛠 技术栈

### 后端
| 技术 | 用途 |
|------|------|
| FastAPI + Uvicorn | Web 框架 |
| PostgreSQL + pgvector | 关系型数据库 + 向量存储 |
| LangChain + LangGraph | LLM 应用框架 |
| Pandas + Scikit-learn | 数据分析与机器学习 |
| Pyecharts | 数据可视化 |
| PyJWT | 身份认证 |

### 前端
| 技术 | 用途 |
|------|------|
| Vue 3 + Vite | 渐进式框架 |
| Element Plus | UI 组件库 |
| ECharts | 交互式图表 |
| Vue Router | 路由管理 |
| Axios | HTTP 客户端 |

---

## ✨ 核心功能

### 数据分析
- 📊 **统计分析** - 描述性统计、分布分析
- 🔍 **关联挖掘** - Apriori 算法发现关联规则
- 🎯 **聚类分析** - K-means 客户分群
- 📉 **时序分析** - 时间序列趋势预测
- 🌪️ **降维分析** - PCA 主成分分析
- 📁 **数据导入** - CSV/Excel 数据上传与管理

### 智能问答
- 💬 **自然语言查询** - Text-to-SQL 将问题转换为 SQL
- 📚 **知识库管理** - RAG 文档上传与检索
- 🔗 **两阶段工作流** - 检索增强 + SQL 查询结合

### 用户系统
- 👤 **用户管理** - 用户增删改查
- 🔐 **权限控制** - 管理员/普通用户角色分离
- 📝 **操作日志** - 用户行为审计

---

## 📦 快速开始

### 环境要求
- Python 3.10+
- Node.js 16+
- PostgreSQL 14+

### 1. 克隆项目
```bash
git clone https://github.com/MarySamos/GR_learn_LG.git
cd BankAgent-Pro
```

### 2. 后端设置
```bash
# 创建虚拟环境
python -m venv .venv
.venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 创建数据库
createdb bank_agent
psql -d bank_agent -c "CREATE EXTENSION vector;"

# 配置 .env 文件
cp backend/.env.example backend/.env
# 编辑 backend/.env 填入 API Key 等配置

# 启动后端
cd backend
python main.py
```

后端地址：http://localhost:8002

### 3. 前端设置
```bash
# 安装依赖
cd frontend
npm install

# 启动开发服务器
npm run dev
```

前端地址：http://localhost:5173

### 默认账号
- 管理员：`admin / admin123`
- 普通用户：注册新用户或使用测试账号

---

## 📂 项目结构

```
BankAgent-Pro/
├── backend/                 # 后端服务
│   ├── app/
│   │   ├── api/            # API 路由
│   │   ├── core/           # 核心配置
│   │   ├── db/             # 数据库连接
│   │   ├── graphs/         # LangGraph 工作流
│   │   ├── schemas/        # 数据模型
│   │   └── services/       # 业务逻辑
│   ├── main.py             # 应用入口
│   └── requirements.txt    # Python 依赖
│
├── frontend/                # 前端应用
│   ├── src/
│   │   ├── assets/         # 静态资源
│   │   ├── components/     # 公共组件
│   │   ├── router/         # 路由配置
│   │   ├── styles/         # 全局样式
│   │   └── views/          # 页面组件
│   │       ├── pages/      # 功能页面
│   │       ├── LoginMinimal.vue
│   │       └── MainLayoutMinimal.vue
│   └── package.json
│
├── data/                    # 数据文件
├── docs/                    # 项目文档
├── logs/                    # 日志文件
├── scripts/                 # 工具脚本
└── CLAUDE.md               # AI 辅助开发配置
```

---

## 🎨 UI 设计

本项目采用 **淡米白纸感主题**，参考 Novel_Assistant 设计语言：

- 暖色调配色系统（深暖棕 + 暖铜色）
- 纸质感卡片与柔和阴影
- macOS 风格浮动 Dock 导航
- 流畅的页面过渡动画

---

## 🚀 开发进度

### 已完成
- [x] 项目架构搭建
- [x] 用户认证与权限系统
- [x] 数据导入与管理模块
- [x] 统计分析模块
- [x] 聚类分析 (K-means)
- [x] 关联规则挖掘 (Apriori)
- [x] PCA 降维分析
- [x] 漏斗分析
- [x] 时序分析与预测
- [x] 知识库管理 (RAG)
- [x] Text-to-SQL 智能问答
- [x] 两阶段工作流集成
- [x] 淡米白纸感 UI 重构
- [x] 浮动 Dock 导航系统

### 进行中
- [ ] 更多预测模型优化
- [ ] 前端响应式适配

---

## 📄 许可证

MIT License

Copyright (c) 2026 MarySamos
