from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings
from . import logger_config
import logging

logger = logging.getLogger(__name__)

DATABASE_URL = f'postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}'

# Establish connection
try:
    engine = create_engine(DATABASE_URL)
    logger.info("Database engine created successfully.")
except Exception as e:
    logger.exception("Failed to create database engine")
    raise e

# Create factory for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    logger.debug("Creating new database session.")
    db = SessionLocal()
    try:
        yield db
    finally:
        logger.debug("Closing database session.")
        db.close()