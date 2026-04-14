# src/ingestion/run_ingestion.py

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from src.ingestion.loader import load_config, load_raw_data
from src.ingestion.preprocessor import preprocess_dataframe, save_processed_data
from src.utils.logger import get_logger

logger = get_logger("ingestion.pipeline")


def run():
    logger.info("=" * 60)
    logger.info("STARTING DATA INGESTION PIPELINE")
    logger.info("=" * 60)

    # Load config
    config = load_config("config/config.yaml")
    raw_path = config["paths"]["raw_data"]
    processed_dir = config["paths"]["processed_data"]

    # Step 1: Load raw data
    logger.info("--- STEP 1: Loading Raw Data ---")
    df = load_raw_data(raw_path)

    # Step 2: Preprocess
    logger.info("--- STEP 2: Preprocessing Text ---")
    df_processed = preprocess_dataframe(df)

    # Step 3: Save
    logger.info("--- STEP 3: Saving Processed Data ---")
    output_path = save_processed_data(df_processed, processed_dir)

    # Summary report
    logger.info("=" * 60)
    logger.info("INGESTION PIPELINE COMPLETE — SUMMARY")
    logger.info("=" * 60)
    logger.info(f"  Total jobs processed     : {len(df_processed)}")
    logger.info(f"  Columns in output        : {list(df_processed.columns)}")
    logger.info(f"  Output saved to          : {output_path}")
    logger.info(f"  Avg description length   : {df_processed['processed_description'].str.split().apply(len).mean():.1f} words")
    logger.info("=" * 60)

    print("\n✅ Ingestion complete! Check logs/ folder for details.")
    print(f"📁 Processed file: {output_path}")
    print(f"📊 Total records: {len(df_processed)}")


if __name__ == "__main__":
    run()
