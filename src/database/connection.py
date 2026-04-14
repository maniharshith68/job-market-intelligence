# src/database/connection.py

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from src.utils.logger import get_logger

load_dotenv()
logger = get_logger("database.connection")


def get_database_url() -> str:
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "jobmarket")
    user = os.getenv("POSTGRES_USER", "admin")
    password = os.getenv("POSTGRES_PASSWORD", "admin123")
    url = f"postgresql://{user}:{password}@{host}:{port}/{db}"
    return url


def get_engine():
    url = get_database_url()
    logger.info(f"Creating database engine for: {url.split('@')[1]}")
    engine = create_engine(url, echo=False, pool_pre_ping=True)
    return engine


def get_session():
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()


def test_connection() -> bool:
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection successful ✅")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False
