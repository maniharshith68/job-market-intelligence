# src/dashboard/app.py

import os
import sys

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


def get_total_jobs() -> int:
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
    logger.info(f"Dashboard initializing with {total_jobs} jobs in DB")
    app.layout = create_layout(total_jobs)
    register_callbacks(app)
    register_resume_callbacks(app)
    return app


# Module-level app and server for gunicorn
app = create_app()
server = app.server


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("STARTING DASHBOARD")
    logger.info("=" * 60)
    app_env = os.getenv("APP_ENV", "development")
    debug_mode = app_env == "development"
    logger.info("Dashboard running at http://localhost:8050")
    app.run(debug=debug_mode, host="0.0.0.0", port=8050)
