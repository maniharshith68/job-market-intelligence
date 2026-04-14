# src/llm/run_scorer.py

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from src.llm.resume_scorer import score_resume
from src.utils.logger import get_logger

logger = get_logger("llm.pipeline")

# ── Sample resume for testing ────────────────────────────────
SAMPLE_RESUME = """
John Smith
Senior Data Scientist | john.smith@email.com | LinkedIn: linkedin.com/in/johnsmith

EXPERIENCE
Senior Data Scientist — TechCorp Inc. (2021–Present)
- Built ML pipelines using Python, Scikit-learn, and XGBoost for fraud detection
- Deployed models to AWS SageMaker, reducing inference time by 40%
- Designed PostgreSQL schemas for feature store management
- Led a team of 3 data scientists using Agile/Scrum methodology

Data Analyst — DataViz Co. (2019–2021)
- Created interactive Tableau dashboards for C-suite reporting
- Wrote complex SQL queries for ETL pipelines in Redshift
- Used Pandas and NumPy for data wrangling and analysis

EDUCATION
M.S. Computer Science — Stanford University (2019)
B.S. Statistics — UC Berkeley (2017)

SKILLS
Python, SQL, PostgreSQL, AWS, Docker, Scikit-learn, XGBoost, Pandas,
NumPy, Tableau, Git, Agile, Machine Learning, Data Engineering
"""

# ── Sample job description for testing ───────────────────────
SAMPLE_JOB = """
Senior Machine Learning Engineer — AI Startup

We are looking for a Senior ML Engineer to join our growing team.

Requirements:
- 4+ years of experience in machine learning or data science
- Strong Python and SQL skills
- Experience with cloud platforms (AWS, GCP, or Azure)
- Familiarity with MLOps tools: MLflow, Kubeflow, or similar
- Experience with deep learning frameworks: PyTorch or TensorFlow
- Knowledge of Kubernetes and Docker for model deployment
- Strong communication and leadership skills
- Experience with Spark or distributed computing is a plus

Responsibilities:
- Design and deploy production ML models at scale
- Build and maintain MLOps pipelines
- Collaborate with product and engineering teams
- Mentor junior engineers
"""


def run():
    logger.info("=" * 60)
    logger.info("STARTING RESUME SCORER TEST")
    logger.info("=" * 60)

    result = score_resume(SAMPLE_RESUME, SAMPLE_JOB)

    logger.info("=" * 60)
    logger.info("RESUME SCORING COMPLETE")
    logger.info("=" * 60)

    print("\n" + "=" * 60)
    print("📊 RESUME FIT SCORE REPORT")
    print("=" * 60)
    print(f"  🎯 Fit Score         : {result.get('fit_score')}/100")
    print(f"  📋 Recommendation    : {result.get('recommendation')}")
    print(f"  🎓 Experience Match  : {result.get('experience_match')}")
    print(f"\n  ✅ Matched Skills:")
    for skill in result.get("matched_skills", []):
        print(f"     • {skill}")
    print(f"\n  ❌ Missing Skills:")
    for skill in result.get("missing_skills", []):
        print(f"     • {skill}")
    print(f"\n  💪 Strengths:")
    print(f"     {result.get('strengths')}")
    print(f"\n  💡 Suggestions:")
    print(f"     {result.get('suggestions')}")
    print("=" * 60)


if __name__ == "__main__":
    run()
