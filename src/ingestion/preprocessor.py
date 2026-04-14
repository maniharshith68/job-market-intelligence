# src/ingestion/preprocessor.py

import re
import os
import sys
import pandas as pd
import spacy

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from src.utils.logger import get_logger

logger = get_logger("ingestion.preprocessor")

# Load spaCy model once at module level
try:
    nlp = spacy.load("en_core_web_sm")
    logger.info("spaCy model 'en_core_web_sm' loaded successfully")
except OSError:
    logger.error("spaCy model not found. Run: python -m spacy download en_core_web_sm")
    raise


CUSTOM_STOPWORDS = {
    "job", "work", "role", "position", "company", "team", "experience",
    "skill", "ability", "knowledge", "requirement", "responsibility",
    "candidate", "applicant", "employer", "employee", "opportunity",
    "strong", "good", "great", "excellent", "preferred", "required",
    "including", "etc", "e.g", "eg", "ie", "must", "will", "able"
}


def clean_text(text: str) -> str:
    """Remove HTML, special characters, digits, and extra whitespace."""
    if not isinstance(text, str):
        return ""
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", text)
    # Remove URLs
    text = re.sub(r"http\S+|www\S+", " ", text)
    # Remove email addresses
    text = re.sub(r"\S+@\S+", " ", text)
    # Remove special characters and digits
    text = re.sub(r"[^a-zA-Z\s]", " ", text)
    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text.lower()


def lemmatize_and_filter(text: str) -> str:
    """Lemmatize tokens and remove stopwords using spaCy."""
    doc = nlp(text)
    tokens = [
        token.lemma_
        for token in doc
        if not token.is_stop
        and not token.is_punct
        and not token.is_space
        and len(token.lemma_) > 2
        and token.lemma_ not in CUSTOM_STOPWORDS
    ]
    return " ".join(tokens)


def preprocess_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Apply full preprocessing pipeline to the DataFrame."""
    logger.info("Starting text preprocessing pipeline...")

    total = len(df)
    logger.info(f"Processing {total} job descriptions...")

    # Step 1: Basic cleaning
    logger.info("Step 1/2: Cleaning text (HTML, special chars, lowercasing)...")
    df["cleaned_description"] = df["job_description"].apply(clean_text)

    # Step 2: Lemmatization + stopword removal
    logger.info("Step 2/2: Lemmatizing and removing stopwords (this may take a minute)...")
    df["processed_description"] = df["cleaned_description"].apply(lemmatize_and_filter)

    # Drop rows where processing resulted in empty strings
    before = len(df)
    df = df[df["processed_description"].str.strip().str.len() > 10].reset_index(drop=True)
    after = len(df)
    if before - after > 0:
        logger.warning(f"Dropped {before - after} rows with empty processed text")

    logger.info(f"Preprocessing complete — final shape: {df.shape}")
    return df


def save_processed_data(df: pd.DataFrame, output_dir: str) -> str:
    """Save processed DataFrame to CSV."""
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "cleaned_jobs.csv")
    df.to_csv(output_path, index=False)
    logger.info(f"Processed data saved to: {output_path}")
    return output_path
