# src/dashboard/app.py

import os
import sys
import threading

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

import dash
import dash_bootstrap_components as dbc
from dash import html
from dotenv import load_dotenv

from src.dashboard.layout import create_layout
from src.dashboard.callbacks import register_callbacks
from src.dashboard.resume_tab import register_resume_callbacks
from src.utils.logger import get_logger

load_dotenv()
logger = get_logger("dashboard.app")

# Global flag to track pipeline status
pipeline_status = {"done": False, "error": None}


def run_pipeline():
    """Run the full NLP pipeline in background thread."""
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

        pipeline_status["done"] = True
        logger.info("Background pipeline complete ✅")

    except Exception as e:
        pipeline_status["error"] = str(e)
        logger.error(f"Background pipeline failed: {e}")


def get_total_jobs():
    """Safely fetch job count, return 0 if DB not ready."""
    try:
        from src.dashboard.data_loader import get_total_job_count
        return get_total_job_count()
    except Exception:
        return 0


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

    # In production, check if pipeline needs to run
    if app_env == "production":
        try:
            from src.database.connection import test_connection
            from src.database.data_loader import get_total_job_count
            conn_ok = test_connection()
            jobs = get_total_jobs()
            if conn_ok and jobs > 0:
                logger.info(f"Database already has {jobs} jobs — skipping pipeline")
                pipeline_status["done"] = True
            else:
                logger.info("Starting background pipeline thread...")
                t = threading.Thread(target=run_pipeline, daemon=True)
                t.start()
        except Exception:
            logger.info("Starting background pipeline thread...")
            t = threading.Thread(target=run_pipeline, daemon=True)
            t.start()
    else:
        pipeline_status["done"] = True

    app = create_app()
    debug_mode = app_env == "development"
    logger.info("Dashboard running at http://localhost:8050")
    app.run(debug=debug_mode, host="0.0.0.0", port=8050)
