# src/nlp/run_nlp.py

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

import yaml
from src.nlp.tfidf_extractor import load_processed_data, extract_tfidf_keywords, save_tfidf_outputs
from src.nlp.bertopic_modeler import run_bertopic
from src.nlp.keyword_trends import compute_keyword_trends, save_keyword_trends
from src.utils.logger import get_logger

logger = get_logger("nlp.pipeline")


def run():
    logger.info("=" * 60)
    logger.info("STARTING NLP PIPELINE")
    logger.info("=" * 60)

    # Load config
    with open("config/config.yaml", "r") as f:
        config = yaml.safe_load(f)

    processed_dir = config["paths"]["processed_data"]
    processed_file = os.path.join(processed_dir, "cleaned_jobs.csv")
    max_features = config["nlp"]["max_features"]
    n_topics = config["nlp"]["n_topics"]
    top_n = config["nlp"]["top_n_skills"]

    # --- STEP 1: TF-IDF ---
    logger.info("--- STEP 1: TF-IDF Keyword Extraction ---")
    df = load_processed_data(processed_file)
    global_keywords, df_with_keywords, vectorizer, tfidf_matrix = extract_tfidf_keywords(
        df, max_features=max_features, top_n=top_n
    )
    save_tfidf_outputs(global_keywords, df_with_keywords, processed_dir)

    logger.info("Top global keywords from TF-IDF:")
    for item in global_keywords:
        logger.info(f"  {item['keyword']:<30} score: {item['mean_tfidf_score']}")

    # --- STEP 2: BERTopic ---
    logger.info("--- STEP 2: BERTopic Topic Modeling ---")
    logger.info("This may take 3-8 minutes on first run...")
    min_topic_size = config["nlp"]["min_topic_size"]
    df_with_topics, topic_info, topic_model = run_bertopic(
        df, n_topics=n_topics, min_topic_size=min_topic_size, output_dir=processed_dir
    )

    # --- STEP 3: Keyword Trends ---
    logger.info("--- STEP 3: Keyword Trends by Job Title ---")
    trends_df = compute_keyword_trends(df_with_keywords, top_n=top_n)
    save_keyword_trends(trends_df, processed_dir)

    # --- Summary ---
    logger.info("=" * 60)
    logger.info("NLP PIPELINE COMPLETE — SUMMARY")
    logger.info("=" * 60)
    logger.info(f"  Records processed        : {len(df)}")
    logger.info(f"  TF-IDF vocab size        : {max_features} features")
    logger.info(f"  Topics discovered        : {df_with_topics['topic_id'].nunique()}")
    logger.info(f"  Unique job titles        : {trends_df['job_title'].nunique()}")
    logger.info(f"  Keyword trend records    : {len(trends_df)}")
    logger.info("=" * 60)

    print("\n✅ NLP Pipeline complete!")
    print(f"📁 Outputs saved to: {processed_dir}")
    print(f"🧠 Topics discovered: {df_with_topics['topic_id'].nunique()}")
    print(f"📊 Unique job titles analyzed: {trends_df['job_title'].nunique()}")


if __name__ == "__main__":
    run()
