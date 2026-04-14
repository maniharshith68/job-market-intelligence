# src/llm/resume_scorer.py

import os
import sys
import json
import re
from groq import Groq
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from src.llm.prompt_builder import build_resume_scoring_prompt
from src.utils.logger import get_logger

load_dotenv()
logger = get_logger("llm.resume_scorer")

MODEL = "llama-3.3-70b-versatile"
MAX_TOKENS = 1024


def get_groq_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables")
    return Groq(api_key=api_key)


def parse_llm_response(response_text: str) -> dict:
    """
    Parse JSON from LLM response robustly.
    Handles cases where model adds extra text around JSON.
    """
    # Try direct parse first
    try:
        return json.loads(response_text.strip())
    except json.JSONDecodeError:
        pass

    # Try extracting JSON block from response
    json_match = re.search(r'\{[\s\S]*\}', response_text)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

    # Return a safe fallback
    logger.warning("Could not parse LLM response as JSON, returning fallback")
    return {
        "fit_score": 0,
        "matched_skills": [],
        "missing_skills": [],
        "strengths": "Could not parse response.",
        "suggestions": "Please try again.",
        "experience_match": "Unknown",
        "recommendation": "Unknown"
    }


def score_resume(resume_text: str, job_description: str) -> dict:
    """
    Score a resume against a job description using Groq LLM.
    Returns a structured dict with fit score and detailed feedback.
    """
    if not resume_text.strip():
        raise ValueError("Resume text cannot be empty")
    if not job_description.strip():
        raise ValueError("Job description cannot be empty")

    logger.info("Building prompt for resume scoring...")
    prompt = build_resume_scoring_prompt(resume_text, job_description)

    logger.info(f"Calling Groq API (model: {MODEL})...")
    client = get_groq_client()

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert technical recruiter. "
                        "Always respond with valid JSON only. "
                        "No markdown, no explanation, just the JSON object."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=MAX_TOKENS,
            temperature=0.3
        )

        raw_response = response.choices[0].message.content
        logger.info("Groq API response received successfully")
        logger.info(f"Tokens used — input: {response.usage.prompt_tokens}, "
                    f"output: {response.usage.completion_tokens}")

        result = parse_llm_response(raw_response)
        logger.info(f"Resume scored — fit score: {result.get('fit_score', 'N/A')}")
        return result

    except Exception as e:
        logger.error(f"Groq API call failed: {e}")
        raise
