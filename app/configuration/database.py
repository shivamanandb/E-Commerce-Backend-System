from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings
from . import logger_config
import logging

logger = logging.getLogger(__name__)

DATABASE_URL = f'postgresql+asyncpg://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}'

# Establish connection
try:
    engine = create_async_engine(DATABASE_URL)
    logger.info("Database engine created successfully.")
except Exception as e:
    logger.exception("Failed to create database engine")
    raise e

# Create factory for database sessions
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session