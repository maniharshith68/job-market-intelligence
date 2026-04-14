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
    host = os.getenv("POSTGRES_HOST", "localhost")
    app_env = os.getenv("APP_ENV", "development")

    logger.info(f"Creating database engine for: {url.split('@')[1]}")

    if app_env == "production" or "supabase" in host:
        connect_args = {
            "sslmode": "require",
            "connect_timeout": 60,
            "keepalives": 1,
            "keepalives_idle": 30,
            "keepalives_interval": 10,
            "keepalives_count": 5
        }
        logger.info("SSL mode enabled for Supabase production database")
    else:
        connect_args = {}

    engine = create_engine(
        url,
        echo=False,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
        pool_timeout=60,
        pool_recycle=300,
        connect_args=connect_args
    )
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
