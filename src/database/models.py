# src/database/models.py

from sqlalchemy import (
    Column, Integer, String, Float, Text,
    DateTime, ForeignKey
)
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()


class JobPosting(Base):
    __tablename__ = "job_postings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_title = Column(String(255), nullable=False)
    job_description = Column(Text, nullable=False)
    cleaned_description = Column(Text, nullable=True)
    processed_description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    skill_extraction = relationship(
        "SkillExtraction", back_populates="job", uselist=False
    )
    topic_assignment = relationship(
        "TopicAssignment", back_populates="job", uselist=False
    )

    def __repr__(self):
        return f"<JobPosting(id={self.id}, title='{self.job_title}')>"


class SkillExtraction(Base):
    __tablename__ = "skill_extractions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey("job_postings.id"), nullable=False)
    extracted_skills = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    job = relationship("JobPosting", back_populates="skill_extraction")

    def __repr__(self):
        return f"<SkillExtraction(job_id={self.job_id})>"


class TopSkill(Base):
    __tablename__ = "top_skills"

    id = Column(Integer, primary_key=True, autoincrement=True)
    rank = Column(Integer, nullable=False)
    skill = Column(String(255), nullable=False, unique=True)
    frequency = Column(Integer, nullable=False)
    category = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<TopSkill(rank={self.rank}, skill='{self.skill}', freq={self.frequency})>"


class KeywordTrend(Base):
    __tablename__ = "keyword_trends"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_title = Column(String(255), nullable=False)
    keyword = Column(String(255), nullable=False)
    frequency = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<KeywordTrend(title='{self.job_title}', keyword='{self.keyword}')>"


class TopicAssignment(Base):
    __tablename__ = "topic_assignments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey("job_postings.id"), nullable=False)
    topic_id = Column(Integer, nullable=False)
    topic_probability = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    job = relationship("JobPosting", back_populates="topic_assignment")

    def __repr__(self):
        return f"<TopicAssignment(job_id={self.job_id}, topic={self.topic_id})>"
