"""
Database Models Definition
定义所有数据库表的 SQLAlchemy 模型
"""
from datetime import datetime, timezone

from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text, Float, ForeignKey, JSON, Index, LargeBinary
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

from app.core.database import Base


# ========== Helper Functions ==========
def _utc_now() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)


# ========== User Model ==========
class User(Base):
    """用户表 - 存储用户信息和权限"""
    __tablename__ = "users"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # User information
    employee_id = Column(String(50), unique=True, index=True, nullable=False, comment="工号")
    name = Column(String(100), nullable=False, comment="姓名")
    department = Column(String(100), comment="部门")
    hashed_password = Column(String(255), nullable=False, comment="密码哈希")

    # Role and status
    role = Column(String(50), nullable=False, default="user", comment="角色: user/admin/analyst")
    is_active = Column(Boolean, default=True, comment="是否激活")

    # Timestamps
    created_at = Column(DateTime, default=_utc_now, comment="创建时间")
    updated_at = Column(DateTime, onupdate=_utc_now, comment="更新时间")

    # Relationships
    operation_logs = relationship("OperationLog", back_populates="user", cascade="all, delete-orphan")


# ========== Marketing Data Model ==========
class MarketingData(Base):
    """
    银行营销数据表 - 存储银行营销活动数据

    兼容两个版本的数据集：
    - 旧版 (bank.csv): 包含 balance, day, deposit 字段
    - 新版 (bank-additional-full.csv): 包含经济指标、day_of_week, y 字段
    """
    __tablename__ = "marketing_data"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # ========== Customer Basic Information ==========
    age = Column(Integer, comment="年龄")
    job = Column(String(50), comment="职业类型")
    marital = Column(String(50), comment="婚姻状况")
    education = Column(String(50), comment="教育程度")
    default_credit = Column(String(10), comment="是否有违约记录")
    balance = Column(Integer, nullable=True, comment="账户余额（旧版数据集）")
    housing = Column(String(50), comment="是否有住房贷款")
    loan = Column(String(50), comment="是否有个人贷款")

    # ========== Contact Information ==========
    contact = Column(String(50), comment="联系方式")
    day = Column(Integer, nullable=True, comment="最后联系日期（旧版数据集）")
    month = Column(String(50), comment="最后联系月份")
    day_of_week = Column(String(50), nullable=True, comment="最后联系星期（新版数据集）")
    duration = Column(Integer, comment="通话时长(秒)")

    # ========== Campaign Information ==========
    campaign = Column(Integer, comment="本次活动联系次数")
    pdays = Column(Integer, comment="距离上次联系天数")
    previous = Column(Integer, comment="之前活动联系次数")
    poutcome = Column(String(50), comment="之前营销结果")

    # ========== Economic Indicators (New Dataset Only) ==========
    emp_var_rate = Column(Float, nullable=True, comment="就业变动率")
    cons_price_idx = Column(Float, nullable=True, comment="消费者物价指数")
    cons_conf_idx = Column(Float, nullable=True, comment="消费者信心指数")
    euribor3m = Column(Float, nullable=True, comment="3个月期欧元银行间同业拆借利率")
    nr_employed = Column(Float, nullable=True, comment="就业人数")

    # ========== Target Variable ==========
    y = Column(String(10), comment="是否订阅定期存款 (yes/no)")

    # ========== Metadata ==========
    created_at = Column(DateTime, default=_utc_now)

    # Indexes
    __table_args__ = (
        Index('ix_marketing_age', 'age'),
        Index('ix_marketing_job', 'job'),
        Index('ix_marketing_y', 'y'),
        Index('ix_marketing_balance', 'balance'),
    )


# ========== Knowledge Document Model ==========
class KnowledgeDoc(Base):
    """知识文档表 - 存储 RAG 用的知识文档"""
    __tablename__ = "knowledge_docs"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Document information
    title = Column(String(255), nullable=False, comment="文档标题")
    content = Column(Text, comment="文档内容")
    file_path = Column(String(500), comment="文件路径")
    file_type = Column(String(50), comment="文件类型 (pdf/txt/md)")

    # pgvector 向量嵌入（1536维 = OpenAI text-embedding-ada-002）
    embedding = Column(Vector(1536), nullable=True, comment="文档向量嵌入 (pgvector)")
    meta_data = Column(JSON, comment="文档元数据")

    # Foreign keys
    uploaded_by = Column(Integer, ForeignKey("users.id"), comment="上传者ID")

    # Timestamps
    created_at = Column(DateTime, default=_utc_now)
    updated_at = Column(DateTime, onupdate=_utc_now)

    # Relationships
    uploader = relationship("User")

    # 索引
    __table_args__ = (
        Index('ix_knowledge_embedding_hnsw', 'embedding',
              postgresql_using='hnsw',
              postgresql_with={'m': 16, 'ef_construction': 64},
              postgresql_ops={'embedding': 'vector_cosine_ops'}),
    )


# ========== Data Table Metadata Model ==========
class DataTable(Base):
    """数据表元数据管理 - 管理系统中的数据表信息"""
    __tablename__ = "data_tables"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Table information
    table_name = Column(String(100), unique=True, nullable=False, comment="表名")
    description = Column(Text, comment="表描述")
    schema_definition = Column(Text, comment="表结构定义 (JSON格式)")
    row_count = Column(Integer, default=0, comment="数据行数")
    is_active = Column(Boolean, default=True, comment="是否启用")

    # Foreign keys
    uploaded_by = Column(Integer, ForeignKey("users.id"), comment="上传者ID")

    # Timestamps
    last_updated = Column(DateTime, default=_utc_now, onupdate=_utc_now)

    # Relationships
    uploader = relationship("User")


# ========== Operation Log Model ==========
class OperationLog(Base):
    """操作日志审计表 - 记录用户操作日志"""
    __tablename__ = "operation_logs"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")

    # Log information
    action = Column(String(100), nullable=False, comment="操作类型")
    resource = Column(String(255), comment="操作资源")
    details = Column(Text, comment="操作详情")
    ip_address = Column(String(50), comment="IP地址")
    status = Column(String(50), comment="操作状态 (success/failed)")

    # Timestamps
    created_at = Column(DateTime, default=_utc_now, index=True)

    # Relationships
    user = relationship("User", back_populates="operation_logs")
