# src/ingestion/loader.py

import pandas as pd
import yaml
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from src.utils.logger import get_logger

logger = get_logger("ingestion.loader")


def load_config(config_path: str = "config/config.yaml") -> dict:
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    logger.info(f"Config loaded from {config_path}")
    return config


def load_raw_data(filepath: str) -> pd.DataFrame:
    logger.info(f"Loading raw data from: {filepath}")

    if not os.path.exists(filepath):
        logger.error(f"File not found: {filepath}")
        raise FileNotFoundError(f"CSV file not found at: {filepath}")

    df = pd.read_csv(filepath)
    logger.info(f"Raw data loaded — shape: {df.shape}")
    logger.info(f"Columns found: {list(df.columns)}")

    # Validate required columns
    required_cols = {"job_title", "job_description"}
    missing = required_cols - set(df.columns)
    if missing:
        logger.error(f"Missing required columns: {missing}")
        raise ValueError(f"Missing columns in CSV: {missing}")

    # Drop fully null rows
    before = len(df)
    df.dropna(subset=["job_title", "job_description"], inplace=True)
    after = len(df)
    logger.info(f"Dropped {before - after} rows with null values")

    # Drop duplicates
    before = len(df)
    df.drop_duplicates(subset=["job_description"], inplace=True)
    after = len(df)
    logger.info(f"Dropped {before - after} duplicate rows")

    # Reset index
    df.reset_index(drop=True, inplace=True)
    logger.info(f"Final loaded shape: {df.shape}")

    return df
