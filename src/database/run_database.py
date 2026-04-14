# src/database/run_database.py

import os
import sys
import yaml
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from src.database.connection import get_engine, get_session, test_connection
from src.database.models import Base
from src.database.inserter import (
    insert_job_postings,
    insert_skill_extractions,
    insert_top_skills,
    insert_keyword_trends,
    insert_topic_assignments
)
from src.utils.logger import get_logger

logger = get_logger("database.pipeline")


def run():
    logger.info("=" * 60)
    logger.info("STARTING DATABASE PIPELINE")
    logger.info("=" * 60)

    # Load config
    with open("config/config.yaml", "r") as f:
        config = yaml.safe_load(f)
    processed_dir = config["paths"]["processed_data"]

    # Step 1: Test connection
    logger.info("--- STEP 1: Testing Database Connection ---")
    if not test_connection():
        logger.error("Cannot connect to PostgreSQL. Is Docker running?")
        raise ConnectionError("PostgreSQL connection failed.")

    # Step 2: Create all tables
    logger.info("--- STEP 2: Creating Tables ---")
    engine = get_engine()
    Base.metadata.create_all(engine)
    logger.info("All tables created successfully ✅")

    # Step 3: Load all CSVs
    logger.info("--- STEP 3: Loading Processed CSVs ---")

    df_jobs = pd.read_csv(os.path.join(processed_dir, "cleaned_jobs.csv"))
    df_skills = pd.read_csv(os.path.join(processed_dir, "ner_skills_per_job.csv"))
    df_top = pd.read_csv(os.path.join(processed_dir, "top10_skills.csv"))
    df_trends = pd.read_csv(os.path.join(processed_dir, "keyword_trends.csv"))
    df_topics = pd.read_csv(os.path.join(processed_dir, "topic_model_results.csv"))

    logger.info(f"  job_postings rows     : {len(df_jobs)}")
    logger.info(f"  skill_extractions rows: {len(df_skills)}")
    logger.info(f"  top_skills rows       : {len(df_top)}")
    logger.info(f"  keyword_trends rows   : {len(df_trends)}")
    logger.info(f"  topic_assignments rows: {len(df_topics)}")

    # Step 4: Insert all data
    logger.info("--- STEP 4: Inserting Data ---")
    session = get_session()

    try:
        index_to_id = insert_job_postings(session, df_jobs)
        insert_skill_extractions(session, df_skills, index_to_id)
        insert_top_skills(session, df_top)
        insert_keyword_trends(session, df_trends)
        insert_topic_assignments(session, df_topics, index_to_id)

    except Exception as e:
        session.rollback()
        logger.error(f"Database insert failed: {e}")
        raise
    finally:
        session.close()

    # Summary
    logger.info("=" * 60)
    logger.info("DATABASE PIPELINE COMPLETE — SUMMARY")
    logger.info("=" * 60)
    logger.info(f"  job_postings inserted     : {len(df_jobs)}")
    logger.info(f"  skill_extractions inserted: {len(df_skills)}")
    logger.info(f"  top_skills inserted       : {len(df_top)}")
    logger.info(f"  keyword_trends inserted   : {len(df_trends)}")
    logger.info(f"  topic_assignments inserted: {len(df_topics)}")
    logger.info("=" * 60)

    print("\n✅ Database pipeline complete!")
    print(f"  📋 Job postings    : {len(df_jobs)}")
    print(f"  🔧 Skill extracts  : {len(df_skills)}")
    print(f"  🏆 Top skills      : {len(df_top)}")
    print(f"  📈 Keyword trends  : {len(df_trends)}")
    print(f"  🧠 Topic assigns   : {len(df_topics)}")


if __name__ == "__main__":
    run()
