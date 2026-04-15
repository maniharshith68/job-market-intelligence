# src/dashboard/app.py

import os
import sys
import threading

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

import dash
import dash_bootstrap_components as dbc
from dotenv import load_dotenv

from src.dashboard.layout import create_layout
from src.dashboard.callbacks import register_callbacks
from src.dashboard.resume_tab import register_resume_callbacks
from src.utils.logger import get_logger

load_dotenv()
logger = get_logger("dashboard.app")

# Module-level flag — prevents double pipeline runs
_pipeline_started = False
_pipeline_lock = threading.Lock()


def run_pipeline():
    """Run the full NLP pipeline in a background thread."""
    try:
        logger.info("Background pipeline starting...")

        from src.ingestion.run_ingestion import run as run_ingestion
        logger.info("Running ingestion...")
        run_ingestion()

        from src.nlp.run_nlp import run as run_nlp
        logger.info("Running NLP...")
        run_nlp()

        from src.nlp.run_ner import run as run_ner
        logger.info("Running NER...")
        run_ner()

        from src.database.run_database import run as run_db
        logger.info("Running database loader...")
        run_db()

        logger.info("Background pipeline complete ✅")

    except Exception as e:
        logger.error(f"Background pipeline failed: {e}")


def get_total_jobs() -> int:
    """Safely fetch job count — returns 0 if DB not ready."""
    try:
        from src.dashboard.data_loader import get_total_job_count
        return get_total_job_count()
    except Exception:
        return 0


def should_run_pipeline() -> bool:
    """Return True if DB is empty and pipeline needs to run."""
    try:
        from src.database.connection import test_connection
        if not test_connection():
            logger.warning("DB connection failed — will run pipeline")
            return True
        jobs = get_total_jobs()
        logger.info(f"DB check: {jobs} jobs found")
        return jobs == 0
    except Exception as e:
        logger.warning(f"Pipeline check error: {e} — will run pipeline")
        return True


def start_pipeline_if_needed():
    """Start the background pipeline thread if DB is empty."""
    global _pipeline_started
    with _pipeline_lock:
        if _pipeline_started:
            logger.info("Pipeline already started — skipping")
            return
        if should_run_pipeline():
            logger.info("DB empty — starting background pipeline thread...")
            t = threading.Thread(target=run_pipeline, daemon=True)
            t.start()
            _pipeline_started = True
        else:
            logger.info("DB already has data — skipping pipeline ✅")
            _pipeline_started = True


def create_app() -> dash.Dash:
    app = dash.Dash(
        __name__,
        external_stylesheets=[
            dbc.themes.BOOTSTRAP,
            "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
        ],
        title="Job Market Intelligence",
        suppress_callback_exceptions=True
    )
    total_jobs = get_total_jobs()
    app.layout = create_layout(total_jobs)
    register_callbacks(app)
    register_resume_callbacks(app)
    return app


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("STARTING DASHBOARD")
    logger.info("=" * 60)

    app_env = os.getenv("APP_ENV", "development")

    if app_env == "production":
        start_pipeline_if_needed()

    app = create_app()
    debug_mode = app_env == "development"
    logger.info("Dashboard running at http://localhost:8050")
    app.run(debug=debug_mode, host="0.0.0.0", port=8050)
