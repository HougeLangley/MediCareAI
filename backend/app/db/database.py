"""
数据库连接和会话管理模块
"""
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text
from app.core.config import settings
from fastapi import HTTPException
import logging
import traceback

logger = logging.getLogger(__name__)

# 异步引擎
engine = create_async_engine(
    settings.database_url,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
)

# 异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

async def get_db():
    """获取数据库会话"""
    db = AsyncSessionLocal()
    try:
        yield db
    except HTTPException:
        # 让 HTTPException 直接传递，不处理
        await db.rollback()
        raise
    except Exception as e:
        error_msg = f"Database error: {type(e).__name__}: {e}"
        logger.error(error_msg)
        logger.error(f"Database URL: {settings.database_url}")
        logger.error(f"Exception details: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        await db.rollback()
        
        raise HTTPException(
            status_code=500,
            detail=f"数据库错误: {str(e)}"
        )
    finally:
        await db.close()

class Base(DeclarativeBase):
    """基础模型类"""
    pass
