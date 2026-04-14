# src/dashboard/app.py

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

import dash
import dash_bootstrap_components as dbc
from dotenv import load_dotenv

from src.dashboard.data_loader import get_total_job_count
from src.dashboard.layout import create_layout
from src.dashboard.callbacks import register_callbacks
from src.utils.logger import get_logger
from src.dashboard.resume_tab import register_resume_callbacks

load_dotenv()
logger = get_logger("dashboard.app")


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

    logger.info("Fetching total job count from database...")
    total_jobs = get_total_job_count()
    logger.info(f"Total jobs: {total_jobs}")

    app.layout = create_layout(total_jobs)
    register_callbacks(app)
    register_resume_callbacks(app)

    return app


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("STARTING DASHBOARD")
    logger.info("=" * 60)
    app = create_app()
    logger.info("Dashboard running at http://localhost:8050")
    app.run(debug=True, host="0.0.0.0", port=8050)
