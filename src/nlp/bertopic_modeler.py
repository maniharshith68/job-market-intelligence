# src/nlp/bertopic_modeler.py

import os
import sys
import pandas as pd
from bertopic import BERTopic
from sklearn.feature_extraction.text import CountVectorizer

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from src.utils.logger import get_logger

logger = get_logger("nlp.bertopic")


def run_bertopic(df: pd.DataFrame, n_topics=10, min_topic_size: int = 3, output_dir: str = "data/processed") -> tuple:
    """
    Fit BERTopic model on processed job descriptions.
    Returns:
        - df with topic assignments
        - topic_info DataFrame
        - fitted BERTopic model
    """
    logger.info("Initializing BERTopic model...")

    corpus = df["processed_description"].tolist()
    logger.info(f"Running BERTopic on {len(corpus)} documents...")

    # Custom vectorizer to clean up topic words
    vectorizer_model = CountVectorizer(
        ngram_range=(1, 2),
        stop_words="english",
        min_df=2
    )

    nr = None if n_topics == "auto" else int(n_topics)
    topic_model = BERTopic(
        language="english",
        calculate_probabilities=True,
        verbose=True,
        vectorizer_model=vectorizer_model,
        nr_topics=nr,
        min_topic_size=min_topic_size
    )

    topics, probs = topic_model.fit_transform(corpus)
    logger.info(f"BERTopic fitting complete — {len(set(topics))} topics found")

    # Assign topics back to df
    df = df.copy()
    df["topic_id"] = topics
    df["topic_probability"] = [round(float(p.max()), 4) if hasattr(p, '__iter__') else round(float(p), 4) for p in probs]

    # Get topic info
    topic_info = topic_model.get_topic_info()
    logger.info(f"Topic info extracted — shape: {topic_info.shape}")

    # Save topic assignments
    os.makedirs(output_dir, exist_ok=True)
    results_path = os.path.join(output_dir, "topic_model_results.csv")
    df[["job_title", "topic_id", "topic_probability"]].to_csv(results_path, index=False)
    logger.info(f"Topic model results saved to: {results_path}")

    # Save topic info
    topic_info_path = os.path.join(output_dir, "topic_info.csv")
    topic_info.to_csv(topic_info_path, index=False)
    logger.info(f"Topic info saved to: {topic_info_path}")

    # Save the fitted model
    model_dir = os.path.join(output_dir, "bertopic_model")
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, "model")
    topic_model.save(model_path)
    logger.info(f"BERTopic model saved to: {model_path}")

    return df, topic_info, topic_model
