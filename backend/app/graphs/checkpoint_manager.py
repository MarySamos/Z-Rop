"""Checkpoint 管理模块.

负责 LangGraph 状态持久化和会话管理

支持两种模式：
1. memory: 内存存储（开发环境，无需额外依赖）
2. postgres: PostgreSQL 持久化（生产环境，需要 psycopg）
"""
from langgraph.checkpoint.memory import MemorySaver

from app.core.config import settings

# 尝试导入 PostgreSQL Checkpointer（可选依赖）
_postgres_available = False
PostgresSaver = None

try:
    from langgraph.checkpoint.postgres import PostgresSaver
    _postgres_available = True
except ImportError:
    PostgresSaver = None
    _postgres_available = False


class CheckpointManager:
    """Checkpoint 管理器（单例模式）"""

    _checkpointer = None

    @classmethod
    def get_checkpointer(cls):
        """获取 Checkpointer 实例.

        支持两种模式：
        1. postgres: PostgreSQL 持久化（如果可用且配置了）
        2. memory: 内存存储（默认）

        Returns:
            Checkpointer 实例
        """
        if cls._checkpointer is None:
            checkpoint_type = settings.CHECKPOINT_TYPE.lower()

            # 尝试使用 PostgreSQL
            if checkpoint_type == "postgres":
                if not _postgres_available:
                    print("[WARN] PostgreSQL checkpoint not available (psycopg not installed)")
                    print("[INFO] Falling back to memory checkpoint storage")
                    print("[INFO] To enable PostgreSQL checkpoint, install: pip install 'psycopg[binary]'")
                    cls._checkpointer = MemorySaver()
                elif not settings.CHECKPOINT_DB_URL:
                    print("[WARN] CHECKPOINT_DB_URL not configured")
                    print("[INFO] Falling back to memory checkpoint storage")
                    cls._checkpointer = MemorySaver()
                else:
                    try:
                        cls._checkpointer = PostgresSaver.from_conn_string(
                            settings.CHECKPOINT_DB_URL
                        )
                        cls._checkpointer.setup()
                        print("[OK] PostgreSQL Checkpoint initialized successfully")
                    except Exception as e:
                        print(f"[ERROR] PostgreSQL Checkpoint initialization failed: {e}")
                        print("[INFO] Falling back to memory checkpoint storage")
                        cls._checkpointer = MemorySaver()
            else:
                cls._checkpointer = MemorySaver()
                print("[OK] Using memory Checkpoint storage")

        return cls._checkpointer


def get_checkpointer():
    """获取 Checkpointer 实例的快捷函数.

    Returns:
        Checkpointer 实例
    """
    return CheckpointManager.get_checkpointer()


# 检查 PostgreSQL 可用性
def is_postgres_available() -> bool:
    """检查 PostgreSQL Checkpointer 是否可用"""
    return _postgres_available
