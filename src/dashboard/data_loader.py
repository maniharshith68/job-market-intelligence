# src/dashboard/data_loader.py

import os
import sys
import pandas as pd
from sqlalchemy import text

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from src.database.connection import get_engine
from src.utils.logger import get_logger

logger = get_logger("dashboard.data_loader")


def get_top_skills() -> pd.DataFrame:
    """Fetch top skills ranked by frequency."""
    engine = get_engine()
    query = text("""
        SELECT rank, skill, frequency, category
        FROM top_skills
        ORDER BY rank ASC
    """)
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    logger.info(f"Fetched {len(df)} top skills")
    return df


def get_keyword_trends(limit: int = 50) -> pd.DataFrame:
    """Fetch top keyword trends across all job titles."""
    engine = get_engine()
    query = text("""
        SELECT keyword, SUM(frequency) as total_frequency
        FROM keyword_trends
        WHERE LENGTH(keyword) > 2
        GROUP BY keyword
        ORDER BY total_frequency DESC
        LIMIT :limit
    """)
    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params={"limit": limit})
    logger.info(f"Fetched {len(df)} keyword trends")
    return df


def get_topic_distribution() -> pd.DataFrame:
    """Fetch topic distribution from BERTopic assignments."""
    engine = get_engine()
    query = text("""
        SELECT topic_id, COUNT(*) as job_count,
               ROUND(AVG(topic_probability)::numeric, 4) as avg_probability
        FROM topic_assignments
        WHERE topic_id >= 0
        GROUP BY topic_id
        ORDER BY job_count DESC
        LIMIT 20
    """)
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    df["topic_label"] = df["topic_id"].apply(lambda x: f"Topic {x}")
    logger.info(f"Fetched {len(df)} topics")
    return df


def get_skill_category_breakdown() -> pd.DataFrame:
    """Fetch skill frequency grouped by category."""
    engine = get_engine()
    query = text("""
        SELECT category, SUM(frequency) as total_frequency
        FROM top_skills
        GROUP BY category
        ORDER BY total_frequency DESC
    """)
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    logger.info(f"Fetched {len(df)} skill categories")
    return df


def get_total_job_count() -> int:
    """Fetch total number of job postings."""
    engine = get_engine()
    query = text("SELECT COUNT(*) as total FROM job_postings")
    with engine.connect() as conn:
        result = conn.execute(query)
        total = result.scalar()
    return total


def get_top_keywords_by_title(job_title: str, limit: int = 10) -> pd.DataFrame:
    """Fetch top keywords for a specific job title."""
    engine = get_engine()
    query = text("""
        SELECT keyword, frequency
        FROM keyword_trends
        WHERE job_title = :title
        ORDER BY frequency DESC
        LIMIT :limit
    """)
    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params={"title": job_title, "limit": limit})
    return df


def get_all_job_titles() -> list:
    """Fetch all unique job titles for dropdown."""
    engine = get_engine()
    query = text("""
        SELECT DISTINCT job_title
        FROM keyword_trends
        ORDER BY job_title ASC
    """)
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    return df["job_title"].tolist()
