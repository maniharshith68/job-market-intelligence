# src/nlp/run_ner.py

import os
import sys
import yaml

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from src.nlp.ner_extractor import (
    load_cleaned_data,
    run_ner_extraction,
    save_ner_outputs
)
from src.utils.logger import get_logger

logger = get_logger("nlp.ner_pipeline")


def run():
    logger.info("=" * 60)
    logger.info("STARTING NER SKILL EXTRACTION PIPELINE")
    logger.info("=" * 60)

    # Load config
    with open("config/config.yaml", "r") as f:
        config = yaml.safe_load(f)

    processed_dir = config["paths"]["processed_data"]
    cleaned_file = os.path.join(processed_dir, "cleaned_jobs.csv")
    top_n = config["nlp"]["top_n_skills"]

    # Step 1: Load data
    logger.info("--- STEP 1: Loading Cleaned Data ---")
    df = load_cleaned_data(cleaned_file)

    # Step 2: Run NER extraction
    logger.info("--- STEP 2: Running NER Skill Extraction ---")
    df_with_skills, skill_counter, top_skills_df = run_ner_extraction(df, top_n=top_n)

    # Step 3: Save outputs
    logger.info("--- STEP 3: Saving NER Outputs ---")
    per_job_path, top10_path = save_ner_outputs(
        df_with_skills, top_skills_df, processed_dir
    )

    # Summary report
    logger.info("=" * 60)
    logger.info("NER PIPELINE COMPLETE — SUMMARY")
    logger.info("=" * 60)
    logger.info(f"  Records processed        : {len(df_with_skills)}")
    logger.info(f"  Total unique skills found: {len(skill_counter)}")
    logger.info(f"  Top {top_n} In-Demand Skills:")
    logger.info("  " + "-" * 45)
    for _, row in top_skills_df.iterrows():
        logger.info(
            f"  #{int(row['rank']):<3} {row['skill']:<30} "
            f"freq: {int(row['frequency']):<6} "
            f"[{row['category']}]"
        )
    logger.info("=" * 60)

    print("\n✅ NER Skill Extraction complete!")
    print(f"📁 Per-job skills : {per_job_path}")
    print(f"🏆 Top {top_n} skills : {top10_path}")
    print(f"\n🔥 Top 10 In-Demand Skills:")
    print("-" * 45)
    for _, row in top_skills_df.iterrows():
        print(f"  #{int(row['rank']):<3} {row['skill']:<28} ({int(row['frequency'])} jobs)")


if __name__ == "__main__":
    run()
