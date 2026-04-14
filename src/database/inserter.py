# src/database/inserter.py

import os
import sys
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from src.utils.logger import get_logger
from src.database.models import (
    JobPosting, SkillExtraction, TopSkill,
    KeywordTrend, TopicAssignment
)

logger = get_logger("database.inserter")


def insert_job_postings(session: Session, df_jobs: pd.DataFrame) -> dict:
    """Insert job postings and return a mapping of index -> db id."""
    logger.info(f"Inserting {len(df_jobs)} job postings...")
    index_to_id = {}
    count = 0

    for idx, row in df_jobs.iterrows():
        job = JobPosting(
            job_title=str(row.get("job_title", ""))[:255],
            job_description=str(row.get("job_description", "")),
            cleaned_description=str(row.get("cleaned_description", "")),
            processed_description=str(row.get("processed_description", ""))
        )
        session.add(job)
        session.flush()  # get the generated id
        index_to_id[idx] = job.id
        count += 1

        if count % 100 == 0:
            logger.info(f"  Inserted {count}/{len(df_jobs)} job postings...")
            session.commit()

    session.commit()
    logger.info(f"Job postings inserted: {count}")
    return index_to_id


def insert_skill_extractions(
    session: Session,
    df_skills: pd.DataFrame,
    index_to_id: dict
) -> int:
    """Insert per-job skill extractions linked to job_postings."""
    logger.info(f"Inserting {len(df_skills)} skill extraction records...")
    count = 0

    for idx, row in df_skills.iterrows():
        job_id = index_to_id.get(idx)
        if job_id is None:
            continue
        extraction = SkillExtraction(
            job_id=job_id,
            extracted_skills=str(row.get("extracted_skills", ""))
        )
        session.add(extraction)
        count += 1

    session.commit()
    logger.info(f"Skill extractions inserted: {count}")
    return count


def insert_top_skills(session: Session, df_top: pd.DataFrame) -> int:
    """Insert top skills — clear existing first to avoid duplicates."""
    logger.info("Clearing existing top_skills table...")
    session.query(TopSkill).delete()
    session.commit()

    logger.info(f"Inserting {len(df_top)} top skills...")
    count = 0

    for _, row in df_top.iterrows():
        skill = TopSkill(
            rank=int(row["rank"]),
            skill=str(row["skill"])[:255],
            frequency=int(row["frequency"]),
            category=str(row.get("category", "other"))[:100]
        )
        session.add(skill)
        count += 1

    session.commit()
    logger.info(f"Top skills inserted: {count}")
    return count


def insert_keyword_trends(session: Session, df_trends: pd.DataFrame) -> int:
    """Insert keyword trends — clear existing first."""
    logger.info("Clearing existing keyword_trends table...")
    session.query(KeywordTrend).delete()
    session.commit()

    logger.info(f"Inserting {len(df_trends)} keyword trend records...")
    count = 0

    for _, row in df_trends.iterrows():
        trend = KeywordTrend(
            job_title=str(row["job_title"])[:255],
            keyword=str(row["keyword"])[:255],
            frequency=int(row["frequency"])
        )
        session.add(trend)
        count += 1

        if count % 500 == 0:
            logger.info(f"  Inserted {count}/{len(df_trends)} keyword trends...")
            session.commit()

    session.commit()
    logger.info(f"Keyword trends inserted: {count}")
    return count


def insert_topic_assignments(
    session: Session,
    df_topics: pd.DataFrame,
    index_to_id: dict
) -> int:
    """Insert BERTopic assignments linked to job_postings."""
    logger.info(f"Inserting {len(df_topics)} topic assignments...")
    count = 0

    for idx, row in df_topics.iterrows():
        job_id = index_to_id.get(idx)
        if job_id is None:
            continue
        assignment = TopicAssignment(
            job_id=job_id,
            topic_id=int(row["topic_id"]),
            topic_probability=float(row.get("topic_probability", 0.0))
        )
        session.add(assignment)
        count += 1

    session.commit()
    logger.info(f"Topic assignments inserted: {count}")
    return count
