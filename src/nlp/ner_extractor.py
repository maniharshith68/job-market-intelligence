# src/nlp/ner_extractor.py

import os
import sys
import pandas as pd
import spacy
from spacy.matcher import PhraseMatcher
from collections import Counter

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from src.utils.logger import get_logger
from src.nlp.skills_vocabulary import get_all_skills, get_skill_category

logger = get_logger("nlp.ner")


def load_cleaned_data(filepath: str) -> pd.DataFrame:
    logger.info(f"Loading cleaned data from: {filepath}")
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    df = pd.read_csv(filepath)
    df.dropna(subset=["cleaned_description"], inplace=True)
    logger.info(f"Loaded {len(df)} records for NER")
    return df


def build_skill_matcher(nlp) -> PhraseMatcher:
    """Build a spaCy PhraseMatcher from the skills vocabulary."""
    logger.info("Building PhraseMatcher from skills vocabulary...")
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    all_skills = get_all_skills()
    patterns = [nlp.make_doc(skill.lower()) for skill in all_skills]
    matcher.add("SKILL", patterns)
    logger.info(f"PhraseMatcher built with {len(all_skills)} skill patterns")
    return matcher


def extract_skills_from_text(text: str, nlp, matcher: PhraseMatcher) -> list:
    """
    Extract skills from a single job description.
    Uses PhraseMatcher for vocabulary-based extraction.
    Also uses NER for ORG/PRODUCT entities as supplementary signals.
    """
    if not isinstance(text, str) or len(text.strip()) == 0:
        return []

    doc = nlp(text[:10000])  # cap at 10k chars for performance
    found_skills = set()

    # --- PhraseMatcher: vocabulary-based skill extraction ---
    matches = matcher(doc)
    for match_id, start, end in matches:
        skill_text = doc[start:end].text
        found_skills.add(skill_text.strip().lower())

    # --- NER: catch PRODUCT/ORG entities that may be tools/frameworks ---
    for ent in doc.ents:
        if ent.label_ in ("PRODUCT", "ORG", "WORK_OF_ART"):
            ent_text = ent.text.strip().lower()
            # Only keep if it's short (likely a tool name, not a company)
            if 2 <= len(ent_text.split()) <= 3 and len(ent_text) > 2:
                found_skills.add(ent_text)

    return list(found_skills)


def run_ner_extraction(df: pd.DataFrame, top_n: int = 10) -> tuple:
    """
    Run NER skill extraction on all job descriptions.
    Returns:
        - df with skills column added
        - global skill counts Counter
        - top_n skills DataFrame
    """
    logger.info("Loading spaCy model for NER...")
    nlp = spacy.load("en_core_web_sm")
    matcher = build_skill_matcher(nlp)

    logger.info(f"Extracting skills from {len(df)} job descriptions...")
    all_skills_flat = []
    per_job_skills = []

    for idx, row in df.iterrows():
        skills = extract_skills_from_text(row["cleaned_description"], nlp, matcher)
        per_job_skills.append(", ".join(skills) if skills else "")
        all_skills_flat.extend(skills)

        if (idx + 1) % 100 == 0:
            logger.info(f"  Processed {idx + 1}/{len(df)} descriptions...")

    logger.info("Skill extraction complete")

    # Add skills column to df
    df = df.copy()
    df["extracted_skills"] = per_job_skills

    # Count global skill frequencies
    skill_counter = Counter(all_skills_flat)
    logger.info(f"Total unique skills found: {len(skill_counter)}")

    # Build top N skills DataFrame
    top_skills = skill_counter.most_common(top_n)
    top_skills_df = pd.DataFrame(top_skills, columns=["skill", "frequency"])
    top_skills_df["rank"] = range(1, len(top_skills_df) + 1)
    top_skills_df["category"] = top_skills_df["skill"].apply(get_skill_category)
    top_skills_df = top_skills_df[["rank", "skill", "frequency", "category"]]

    logger.info(f"Top {top_n} skills identified")

    return df, skill_counter, top_skills_df


def save_ner_outputs(df: pd.DataFrame, top_skills_df: pd.DataFrame, output_dir: str) -> tuple:
    """Save NER results to CSV files."""
    os.makedirs(output_dir, exist_ok=True)

    # Save per-job skills
    per_job_path = os.path.join(output_dir, "ner_skills_per_job.csv")
    df[["job_title", "extracted_skills"]].to_csv(per_job_path, index=False)
    logger.info(f"Per-job skills saved to: {per_job_path}")

    # Save top 10 skills
    top10_path = os.path.join(output_dir, "top10_skills.csv")
    top_skills_df.to_csv(top10_path, index=False)
    logger.info(f"Top skills saved to: {top10_path}")

    return per_job_path, top10_path
