# src/nlp/keyword_trends.py

import os
import sys
import pandas as pd
from collections import Counter

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from src.utils.logger import get_logger

logger = get_logger("nlp.keyword_trends")


def compute_keyword_trends(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Group by job_title and compute top keywords per role.
    Returns a DataFrame with job_title and their top keywords.
    """
    logger.info("Computing keyword trends by job title...")

    records = []

    for title, group in df.groupby("job_title"):
        all_words = []
        for desc in group["processed_description"].dropna():
            all_words.extend(desc.split())

        # Count word frequencies
        counter = Counter(all_words)
        top_keywords = counter.most_common(top_n)

        for keyword, freq in top_keywords:
            records.append({
                "job_title": title,
                "keyword": keyword,
                "frequency": freq
            })

    trends_df = pd.DataFrame(records)
    logger.info(f"Keyword trends computed — {len(trends_df)} records across {trends_df['job_title'].nunique()} job titles")
    return trends_df


def save_keyword_trends(trends_df: pd.DataFrame, output_dir: str) -> str:
    """Save keyword trends to CSV."""
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "keyword_trends.csv")
    trends_df.to_csv(output_path, index=False)
    logger.info(f"Keyword trends saved to: {output_path}")
    return output_path
