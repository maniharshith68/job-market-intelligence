# src/nlp/tfidf_extractor.py

import os
import sys
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from src.utils.logger import get_logger

logger = get_logger("nlp.tfidf")


def load_processed_data(filepath: str) -> pd.DataFrame:
    logger.info(f"Loading processed data from: {filepath}")
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    df = pd.read_csv(filepath)
    df.dropna(subset=["processed_description"], inplace=True)
    logger.info(f"Loaded {len(df)} records")
    return df


def extract_tfidf_keywords(df: pd.DataFrame, max_features: int = 500, top_n: int = 10) -> tuple:
    """
    Fit TF-IDF on all job descriptions.
    Returns:
        - global_keywords: top N keywords across entire corpus
        - per_job_keywords: top N keywords per job row
        - vectorizer: fitted TfidfVectorizer
        - tfidf_matrix: full matrix
    """
    logger.info(f"Fitting TF-IDF vectorizer (max_features={max_features})...")

    vectorizer = TfidfVectorizer(
        max_features=max_features,
        ngram_range=(1, 2),       # unigrams + bigrams
        min_df=2,                  # must appear in at least 2 docs
        max_df=0.90,               # ignore terms in >90% of docs
        sublinear_tf=True          # apply log normalization
    )

    corpus = df["processed_description"].tolist()
    tfidf_matrix = vectorizer.fit_transform(corpus)
    feature_names = vectorizer.get_feature_names_out()

    logger.info(f"TF-IDF matrix shape: {tfidf_matrix.shape}")
    logger.info(f"Vocabulary size: {len(feature_names)}")

    # --- Global top keywords (mean TF-IDF score across all docs) ---
    mean_scores = np.asarray(tfidf_matrix.mean(axis=0)).flatten()
    top_indices = mean_scores.argsort()[::-1][:top_n]
    global_keywords = [
        {"keyword": feature_names[i], "mean_tfidf_score": round(float(mean_scores[i]), 6)}
        for i in top_indices
    ]
    logger.info(f"Top {top_n} global keywords extracted")

    # --- Per-job top keywords ---
    logger.info("Extracting per-job top keywords...")
    per_job_keywords = []
    matrix_array = tfidf_matrix.toarray()

    for idx, row_scores in enumerate(matrix_array):
        top_idx = row_scores.argsort()[::-1][:top_n]
        keywords = [feature_names[i] for i in top_idx if row_scores[i] > 0]
        per_job_keywords.append(", ".join(keywords))

    df = df.copy()
    df["tfidf_keywords"] = per_job_keywords

    return global_keywords, df, vectorizer, tfidf_matrix


def save_tfidf_outputs(global_keywords: list, df: pd.DataFrame, output_dir: str) -> tuple:
    """Save global keywords and per-job keywords to CSV."""
    os.makedirs(output_dir, exist_ok=True)

    # Save global keywords
    global_path = os.path.join(output_dir, "tfidf_global_keywords.csv")
    pd.DataFrame(global_keywords).to_csv(global_path, index=False)
    logger.info(f"Global keywords saved to: {global_path}")

    # Save per-job keywords (append to existing df)
    perjob_path = os.path.join(output_dir, "tfidf_keywords.csv")
    df[["job_title", "tfidf_keywords"]].to_csv(perjob_path, index=False)
    logger.info(f"Per-job keywords saved to: {perjob_path}")

    return global_path, perjob_path
