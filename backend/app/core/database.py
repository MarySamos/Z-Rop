"""Database Connection Configuration.

Creates SQLAlchemy engine and session management.
"""
import logging
from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.core.config import settings

# Database connection pool constants
_POOL_SIZE = 5
_MAX_OVERFLOW = 10
_HEALTH_CHECK_QUERY = text("SELECT 1")

logger = logging.getLogger(__name__)

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=_POOL_SIZE,
    max_overflow=_MAX_OVERFLOW,
    echo=settings.DEBUG,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Database session dependency injection for FastAPI.

    Yields:
        Session: Database session

    Raises:
        SQLAlchemyError: When database connection fails
    """
    db = SessionLocal()
    try:
        db.execute(_HEALTH_CHECK_QUERY)
        yield db
    except SQLAlchemyError as e:
        logger.error(f"Database connection failed: {e}")
        raise
    finally:
        db.close()
