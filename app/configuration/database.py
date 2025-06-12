from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings
from . import logger_config
import logging

# set up logger
logger = logging.getLogger(__name__)

# Build the PostgreSQL async connection string
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

# Base class for model Declaration
Base = declarative_base()

# Dependency function to be used with FastAPI routes
# This provides a new session for each request and automatically closes it after use
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session