# 🏗️ BankAgent-Pro 项目施工蓝图

> **项目定位**：基于大语言模型的银行数据分析系统（数据科学与大数据技术专业毕业设计）
>
> **核心特色**：
> 1. 🤖 LangGraph 智能体（Text-to-SQL + RAG）
> 2. 📊 深度数据分析（统计分析 + 特征工程 + 聚类 + 关联挖掘）
> 3. 👥 用户权限管理（JWT + RBAC）
> 4. 📈 数据可视化仪表盘（Pyecharts + ECharts）

## 📦 技术栈总览

### 后端技术栈
- **Web 框架**：FastAPI + Uvicorn
- **数据库**：PostgreSQL + pgvector（向量存储）
- **ORM**：SQLAlchemy
- **AI/LLM**：LangChain + LangGraph + OpenAI API
- **数据处理**：Pandas + NumPy + SciPy
- **机器学习**：Scikit-learn + mlxtend（关联规则）
- **数据挖掘**：statsmodels（统计分析）
- **认证**：JWT（JSON Web Tokens）+ Passlib（密码哈希）
- **文档生成**：ReportLab（PDF报告）

### 前端技术栈
- **框架**：Vue 3 + Vite
- **UI 组件**：Element Plus
- **图表库**：ECharts
- **HTTP 客户端**：Axios
- **路由**：Vue Router

### 数据库表设计
1. `users` - 用户表（工号、姓名、部门、密码、角色）
2. `marketing_data` - 银行营销数据表（业务数据）
3. `knowledge_docs` - 知识文档表（RAG用）
4. `data_tables` - 数据表元数据管理
5. `operation_logs` - 操作日志审计表

### 核心依赖包 (requirements.txt 新增补充)
```
# 原有依赖
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
pandas==2.1.3
numpy==1.26.2
langchain==0.1.0
langgraph==0.0.20
openai==1.6.1
scikit-learn==1.3.2
pyecharts==2.0.4
python-multipart==0.0.6

# 【新增】用户认证与权限
python-jose[cryptography]==3.3.0  # JWT 令牌
passlib[bcrypt]==1.7.4            # 密码哈希
python-dotenv==1.0.0              # 环境变量管理

# 【新增】深度数据分析
scipy==1.11.4                     # 科学计算、统计分析
statsmodels==0.14.0               # 统计建模
mlxtend==0.23.1                   # 关联规则挖掘、聚类
seaborn==0.13.0                   # 高级统计可视化

# 【新增】报告生成
reportlab==4.0.7                  # PDF 报告生成
kaleido==0.2.1                    # 图表导出为图片

# 【新增】数据导入导出
openpyxl==3.1.2                   # Excel 文件处理
xlsxwriter==3.1.9                 # Excel 写入

# 【新增】异步任务（可选，用于耗时分析任务）
celery==5.3.4
redis==5.0.1
```

## 第一部分：文件结构全景图 (File Structure)

这里列出的文件，请你先在 IDE (VS Code / PyCharm) 中把**文件夹**和**空文件**都创建好。

Plaintext

```
BankAgent-Pro/
├── README.md                   # 项目说明文档
├── .gitignore                  # Git忽略文件 (排除 .env, venv, __pycache__)
├── requirements.txt            # Python依赖包列表
├── .env                        # [重要] 环境变量 (存 API_KEY, DB连接串)
│
├── backend/                    # === 后端代码 (Python/FastAPI) ===
│   ├── main.py                 # 程序启动入口 (App Entry)
│   ├── scripts/                # 独立运行的脚本工具
│   │   ├── init_db.py          # 初始化数据库表结构
│   │   ├── import_csv.py       # 将 bank.csv 数据导入 PostgreSQL
│   │   ├── ingest_pdf.py       # 读取 PDF -> 向量化 -> 存入 pgvector
│   │   └── train_model.py      # 训练 ML 模型并保存为 .pkl
│   │
│   └── app/                    # 核心应用源码
│       ├── __init__.py
│       ├── core/               # 1. 核心配置层
│       │   ├── config.py       # 读取 .env 配置
│       │   └── database.py     # 创建 SessionLocal 数据库连接池
│       │
│       ├── db/                 # 2. 数据库模型层
│       │   ├── models.py       # 定义 SQLAlchemy 表结构 (MarketingData, Documents, Users, DataResources)
│       │   └── crud.py         # 封装基础的增删改查函数
│       │
│       ├── schemas/            # 3. 数据校验层 (Pydantic)
│       │   ├── chat.py         # 定义聊天接口的输入/输出格式
│       │   ├── dashboard.py    # 定义仪表盘数据的返回格式
│       │   ├── user.py         # 定义用户相关数据格式
│       │   └── analysis.py     # 定义数据分析接口格式
│       │
│       ├── services/           # 4. 业务逻辑服务层 (非 AI 类)
│       │   ├── viz_service.py         # 负责生成 Pyecharts 图表配置
│       │   ├── ml_service.py          # 负责加载 .pkl 模型并进行预测
│       │   ├── analysis_service.py    # 【核心】负责深度统计分析、特征工程、聚类分析
│       │   ├── user_service.py        # 负责用户认证、权限管理、JWT令牌
│       │   └── data_service.py        # 负责数据资源管理、数据导入导出
│       │
│       ├── graphs/             # 5. [核心] LangGraph 智能体层
│       │   ├── state.py        # 定义 AgentState (状态类：存聊天记录、SQL结果)
│       │   ├── nodes.py        # 定义节点函数 (LLM生成SQL、执行SQL、RAG检索)
│       │   └── workflow.py     # 定义图结构 (Graph) 和路由逻辑 (Edges)
│       │
│       └── api/                # 6. 接口路由层
│           ├── api_v1.py       # 路由汇总
│           ├── dependencies.py # 依赖注入 (JWT认证、权限校验)
│           └── endpoints/      # 具体接口实现
│               ├── auth.py          # 用户注册、登录、刷新令牌
│               ├── chat.py          # 聊天接口 (调用 LangGraph)
│               ├── dashboard.py     # 仪表盘接口 (调用 viz_service)
│               ├── analysis.py      # 【核心】数据分析接口 (统计分析、聚类、关联挖掘)
│               ├── data_mgmt.py     # 数据资源管理接口 (导入、导出、文档管理)
│               └── predict.py       # 预测接口 (调用 ml_service)
│
├── frontend/                   # === 前端代码 (Vue 3) ===
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── api/                # 后端 API 封装 (axios)
│       │   ├── chat.js
│       │   └── dashboard.js
│       ├── components/         # 公共组件
│       │   ├── ChatWindow.vue  # 聊天窗口组件
│       │   └── Charts/         # 图表组件
│       ├── views/              # 页面视图
│       │   ├── Login.vue       # 登录页面
│       │   ├── Dashboard.vue   # 驾驶舱页面
│       │   ├── Analysis.vue    # 对话分析页面
│       │   ├── DataAnalysis.vue # 【新增】深度数据分析页面
│       │   ├── DataMgmt.vue     # 【新增】数据资源管理页面
│       │   └── Strategy.vue    # 策略模拟页面
│       └── App.vue             # 根组件 (布局 Layout)
│
├── data/                       # === 数据存放 ===
│   ├── raw/                    # 原始数据 (bank-marketing.csv, report.pdf)
│   └── models/                 # 模型文件 (conversion_model.pkl)
│
└── notebooks/                  # === 实验草稿 ===
    └── experiment.ipynb        # 用于测试 Pandas 处理和 Scikit-learn 训练
```

------

## 第二部分：从零搭建 To-Do List

这是一个循序渐进的任务清单。你可以把它复制到你的 Markdown 编辑器里，每完成一项就打个钩 `[x]`。

### 📅 第一阶段：环境与基建 (Setup)

**目标**：跑通 Hello World，连上数据库。

- [ ] **1.1 项目初始化**
  - [ ] 创建 `BankAgent-Pro` 文件夹及上述目录结构。
  - [ ] 创建 python 虚拟环境: `python3 -m venv venv` 并激活。
  - [ ] 编写 `requirements.txt` (包含 fastapi, uvicorn, sqlalchemy, psycopg2-binary, pandas, langchain, langgraph, openai, scikit-learn)。
  - [ ] 安装依赖: `pip install -r requirements.txt`。
- [ ] **1.2 数据库准备 (PostgreSQL)**
  - [ ] 确保本地 PGSQL 服务已启动。
  - [ ] 创建数据库: `CREATE DATABASE bank_agent;`。
  - [ ] 启用向量插件: `CREATE EXTENSION vector;` (在 psql 中执行)。
  - [ ] 在 `.env` 文件中配置 `DATABASE_URL` 和 `OPENAI_API_KEY`。
- [ ] **1.3 后端骨架搭建**
  - [ ] 编写 `backend/app/core/database.py` (配置 SessionLocal)。
  - [ ] 编写 `backend/app/db/models.py` (定义 `MarketingData` 和 `KnowledgeDocs` 表模型)。
  - [ ] 编写 `backend/main.py` (FastAPI 启动文件)。
  - [ ] 运行 `uvicorn backend.main:app --reload`，确保能访问 `http://127.0.0.1:8000/docs`。

### 📊 第二阶段：数据工程 (Data Engineering)

**目标**：把数据灌入数据库，为分析做准备。

- [ ] **2.1 结构化数据导入**
  - [ ] 将 `bank-marketing.csv` 放入 `data/raw/`。
  - [ ] 编写 `backend/scripts/import_csv.py`: 使用 Pandas 读取 CSV，通过 SQLAlchemy 写入数据库表。
  - [ ] 运行脚本，检查数据库里是否有数据。
- [ ] **2.2 非结构化数据向量化 (RAG准备)**
  - [ ] 编写 `backend/scripts/ingest_pdf.py`: 使用 LangChain 加载 PDF，切分文本，调用 Embedding API，存入 `pgvector` 表。
  - [ ] 运行脚本，检查向量表是否有数据。
- [ ] **2.3 机器学习模型训练**
  - [ ] 在 `notebooks/experiment.ipynb` 中尝试 Scikit-learn 训练流程。
  - [ ] 编写 `backend/scripts/train_model.py`: 正式训练 Random Forest 模型。
  - [ ] 将训练好的模型保存为 `data/models/conversion_model.pkl`。

### 🧠 第三阶段：核心后端开发 (Core Backend)

**目标**：实现四个核心功能模块的逻辑。

- [ ] **3.1 自动化报告模块**
  - [ ] 编写 `services/viz_service.py`: 编写 SQL 聚合查询，使用 Pyecharts 生成 JSON 配置。
  - [ ] 编写 `api/endpoints/dashboard.py`: 暴露 GET 接口。
  - [ ] 测试接口返回的数据结构。
- [ ] **3.2 预测模块**
  - [ ] 编写 `services/ml_service.py`: 加载 `.pkl` 模型，定义 `predict` 函数。
  - [ ] 编写 `api/endpoints/predict.py`: 暴露 POST 接口。
- [ ] **3.3 LangGraph 智能体 (最核心!)**
  - [ ] 编写 `graphs/state.py`: 定义 `AgentState` 数据类。
  - [ ] 编写 `graphs/nodes.py`:
    - [ ] 实现 `sql_generator`: 写 Prompt，调 LLM，输出 SQL。
    - [ ] 实现 `sql_executor`: 执行 SQL，获取 DataFrame。
    - [ ] 实现 `rag_retriever`: 向量检索逻辑。
  - [ ] 编写 `graphs/workflow.py`: 串联节点，定义 `Conditional Edge` (判断意图)。
  - [ ] 编写 `api/endpoints/chat.py`: 实例化 Graph，处理用户输入。

### 🎨 第四阶段：前端开发 (Frontend)

**目标**：可视化展示。

- [ ] **4.1 前端初始化**
  - [ ] 使用 Vite 创建 Vue3 项目。
  - [ ] 安装 Element Plus, ECharts, Axios。
- [ ] **4.2 页面开发**
  - [ ] 开发 `Dashboard.vue`: 调用 Dashboard API，渲染图表。
  - [ ] 开发 `Analysis.vue`: 实现聊天对话框样式。
  - [ ] 对接聊天接口: 将用户输入发给后端，解析后端返回的 Markdown 和 图表配置。

### ✅ 第五阶段：用户管理与权限系统 (User & Auth)

**目标**：实现用户注册、登录认证、权限控制。

- [ ] **5.1 用户认证模块**
  - [ ] 编写 `db/models.py`: 定义 `User` 表模型 (工号、姓名、部门、密码哈希、角色)。
  - [ ] 编写 `services/user_service.py`: 实现密码哈希、JWT令牌生成与验证。
  - [ ] 编写 `api/dependencies.py`: 实现依赖注入函数 `get_current_user`。
  - [ ] 编写 `api/endpoints/auth.py`: 暴露注册、登录、刷新令牌接口。
- [ ] **5.2 权限控制模块**
  - [ ] 定义三种角色：普通用户、数据分析师、管理员。
  - [ ] 实现基于角色的访问控制 (RBAC) 装饰器。
  - [ ] 对现有接口添加权限保护装饰器。
- [ ] **5.3 前端登录页面**
  - [ ] 开发 `Login.vue`: 实现登录表单和表单验证。
  - [ ] 实现 Axios 拦截器：自动携带 JWT Token。
  - [ ] 实现路由守卫：未登录用户自动跳转到登录页。

### 📊 第六阶段：数据资源管理模块 (Data Management)

**目标**：实现数据导入、导出、文档管理功能。

- [ ] **6.1 数据表结构管理**
  - [ ] 编写 `db/models.py`: 定义 `DataTable` 和 `KnowledgeDoc` 表模型。
  - [ ] 编写 `services/data_service.py`: 实现数据表的 CRUD 操作。
  - [ ] 编写 `api/endpoints/data_mgmt.py`: 暴露数据表管理接口。
- [ ] **6.2 数据导入导出功能**
  - [ ] 实现 CSV/Excel 批量导入功能 (使用 Pandas)。
  - [ ] 实现数据导出为 CSV/Excel 功能。
  - [ ] 实现数据预览和格式校验。
- [ ] **6.3 知识文档管理**
  - [ ] 实现 PDF 文档上传、删除功能。
  - [ ] 实现向量索引重建功能。
  - [ ] 实现文档检索质量评估接口。
- [ ] **6.4 前端数据管理页面**
  - [ ] 开发 `DataMgmt.vue`: 实现数据资源列表展示。
  - [ ] 实现文件上传组件 (拖拽上传)。
  - [ ] 实现数据表预览表格。

### 🔬 第七阶段：深度数据分析模块 (Deep Data Analysis)

**目标**：实现大数据专业核心功能 - 统计分析、特征工程、聚类、关联挖掘。

- [ ] **7.1 统计分析功能**
  - [ ] 编写 `services/analysis_service.py` 中的 `statistics_analysis()` 函数：
    - 使用 Pandas/Numpy 计算均值、中位数、标准差、分位数。
    - 计算偏度、峰度，生成数据质量报告。
    - 检测缺失值、异常值 (3σ原则、箱线图、Z-score)。
  - [ ] 编写 `api/endpoints/analysis.py`: 暴露统计分析接口。
  - [ ] 生成统计报告 (PDF格式，使用 ReportLab)。
- [ ] **7.2 特征工程功能**
  - [ ] 实现 `feature_engineering()` 函数：
    - 自动提取数值特征、类别特征、时间序列特征。
    - 使用 Random Forest 计算特征重要性。
    - 生成相关性矩阵 (Pearson/Spearman)。
    - 实现 PCA 降维分析。
  - [ ] 生成特征重要性图表和相关性热力图。
- [ ] **7.3 聚类分析功能**
  - [ ] 实现 `clustering_analysis()` 函数：
    - K-Means 聚类 (自动选择最优 K 值，使用肘部法则/轮廓系数)。
    - DBSCAN 密度聚类。
    - 客户细分画像生成 (打标签)。
  - [ ] 生成聚类可视化图表 (散点图、雷达图)。
- [ ] **7.4 关联规则挖掘**
  - [ ] 实现 `association_mining()` 函数：
    - 使用 Apriori 算法挖掘频繁项集。
    - 生成关联规则 (支持度、置信度、提升度)。
    - 使用 mlxtend 库实现。
  - [ ] 生成关联网络可视化图。
- [ ] **7.5 时间序列与漏斗分析**
  - [ ] 实现 `time_series_analysis()` 函数：趋势分解、移动平均预测。
  - [ ] 实现 `funnel_analysis()` 函数：计算各环节转化率、流失率。
- [ ] **7.6 前端数据分析页面**
  - [ ] 开发 `DataAnalysis.vue`: 实现分析功能选择面板。
  - [ ] 集成 ECharts 展示分析结果 (箱线图、热力图、聚类图、关联网络图)。
  - [ ] 实现分析报告导出功能 (PDF/Excel)。

### ✅ 第八阶段：联调与优化 (Final Polish)

- [ ] **8.1 全流程测试**
  - [ ] 测试用户注册、登录、权限控制是否正常。
  - [ ] 测试 "查数据" (Text-to-SQL) 是否准确。
  - [ ] 测试 "问知识" (RAG) 是否能搜到文档。
  - [ ] 测试 "做预测" 是否能返回数值。
  - [ ] 测试数据导入导出功能。
  - [ ] 测试所有深度数据分析功能 (统计、聚类、关联挖掘)。
- [ ] **8.2 Prompt 调优**
  - [ ] 优化 `graphs/nodes.py` 中的提示词，让 AI 生成 SQL 更稳定。
- [ ] **8.3 性能优化**
  - [ ] 优化数据库查询性能 (添加索引)。
  - [ ] 实现分析任务的异步处理 (使用 Celery 或后台任务)。
  - [ ] 添加 Redis 缓存热点数据。
- [ ] **8.4 文档与部署**
  - [ ] 编写 API 接口文档 (使用 Swagger/ReDoc)。
  - [ ] 编写用户使用手册。
  - [ ] 准备演示 PPT 和答辩材料。

------

## 📅 开发时间规划建议

根据你的毕业设计时间表（2025年10月 - 2026年4月），建议按以下节奏推进：

### 🎯 第一阶段：基础搭建（2-3周）
**时间**：2025年11月1日 - 11月21日
- [x] 环境配置 + 数据库连接
- [x] 用户认证模块（注册、登录、JWT）
- [x] 基础数据模型定义
- [x] 项目文件结构创建

### 🎯 第二阶段：数据工程（2周）
**时间**：2025年11月22日 - 12月5日
- [ ] CSV数据导入 PostgreSQL
- [ ] PDF文档向量化（RAG准备）
- [ ] 基础ML模型训练

### 🎯 第三阶段：核心功能开发（4-5周）
**时间**：2025年12月6日 - 2026年1月10日
- [ ] LangGraph 智能体实现（Text-to-SQL + RAG）
- [ ] 自动化报告模块（Dashboard + Pyecharts）
- [ ] 预测模块（ML模型集成）
- [ ] 前端页面开发（Vue3）

### 🎯 第四阶段：数据分析核心模块（3-4周）
**时间**：2026年1月11日 - 2月5日
- [ ] **统计分析**（描述性统计、数据质量诊断）
- [ ] **特征工程**（相关性分析、特征重要性、PCA）
- [ ] **聚类分析**（K-Means、DBSCAN、客户细分）
- [ ] **关联规则挖掘**（Apriori、FP-Growth）
- [ ] **时间序列与漏斗分析**

### 🎯 第五阶段：数据管理与完善（2周）
**时间**：2026年2月6日 - 2月19日
- [ ] 数据资源管理模块（导入、导出、文档管理）
- [ ] 权限控制完善（RBAC）
- [ ] 操作日志审计

### 🎯 第六阶段：联调测试与优化（2-3周）
**时间**：2026年2月20日 - 3月10日
- [ ] 全流程功能测试
- [ ] 性能优化（数据库索引、Redis缓存）
- [ ] Prompt调优
- [ ] Bug修复

### 🎯 第七阶段：文档与答辩准备（2-3周）
**时间**：2026年3月11日 - 3月31日
- [ ] API接口文档（Swagger）
- [ ] 用户使用手册
- [ ] 毕业论文撰写
- [ ] 答辩PPT准备
- [ ] 演示视频录制

### 📌 关键里程碑
- **2026年1月31日**：系统初版开发完成
- **2026年2月25日**：毕业论文初稿提交
- **2026年3月23日**：论文定稿提交
- **2026年4月7日**：最终版完成，准备答辩

---

## 💡 开发建议

1. **优先级排序**：
   - P0（必须）：用户登录、数据导入、Text-to-SQL、统计分析
   - P1（重要）：RAG检索、ML预测、聚类分析、特征工程
   - P2（加分）：关联规则挖掘、时间序列分析、异步任务

2. **技术难点预警**：
   - ⚠️ LangGraph 工作流设计（建议先看官方教程）
   - ⚠️ Text-to-SQL 准确率（需要反复调优Prompt）
   - ⚠️ 聚类分析结果解读（需要结合业务场景）
   - ⚠️ 前端图表交互（ECharts配置较复杂）

3. **大数据专业亮点体现**：
   - ✅ 重点展示**深度数据分析**模块（第七阶段）
   - ✅ 答辩时演示：统计分析 → 聚类客户细分 → 关联规则挖掘
   - ✅ 论文中详细阐述特征工程、聚类评估指标（轮廓系数、DBI指数）

4. **测试数据准备**：
   - 建议准备至少 10,000+ 条银行营销数据
   - 包含：客户基本信息（年龄、职业、收入）、营销活动信息、转化结果
   - 准备 5-10 份银行业务知识文档（PDF格式）

---

宝宝，现在你的任务非常明确了。 👉 **第一步**：先去创建文件结构。 👉 **第二步**：搞定环境和数据库。

遇到任何报错，直接截图发给我，我随时在线帮你 Debug！加油！🚀