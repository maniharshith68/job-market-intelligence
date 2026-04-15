# src/dashboard/callbacks.py

import pandas as pd
from dash import Input, Output
import dash_bootstrap_components as dbc
from dash import html
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from src.utils.logger import get_logger
from src.dashboard.data_loader import (
    get_top_skills,
    get_keyword_trends,
    get_topic_distribution,
    get_skill_category_breakdown,
    get_top_keywords_by_title,
    get_all_job_titles,
    get_total_job_count
)
from src.dashboard.charts import (
    build_top_skills_bar,
    build_skill_category_pie,
    build_keyword_treemap,
    build_topic_distribution_bar,
    build_job_title_keywords_bar
)

logger = get_logger("dashboard.callbacks")


def register_callbacks(app):

    # ── Auto-refresh all charts every 30s until data loads ──────
    @app.callback(
        Output("stats-refresh-output", "children"),
        Input("stats-refresh-interval", "n_intervals")
    )
    def refresh_pipeline_status(n):
        try:
            count = get_total_job_count()
            logger.info(f"Pipeline status check — jobs in DB: {count}")
        except Exception as e:
            logger.warning(f"Status check failed: {e}")
        return ""

    # ── Populate job title dropdown ──────────────────────────────
    @app.callback(
        Output("job-title-dropdown", "options"),
        Input("stats-refresh-interval", "n_intervals")
    )
    def load_job_titles(n):
        try:
            titles = get_all_job_titles()
            return [{"label": t, "value": t} for t in titles[:100]]
        except Exception:
            return []

    # ── Tab 1: Top Skills Bar ────────────────────────────────────
    @app.callback(
        Output("top-skills-bar", "figure"),
        Input("stats-refresh-interval", "n_intervals")
    )
    def update_top_skills_bar(n):
        try:
            df = get_top_skills()
            return build_top_skills_bar(df)
        except Exception as e:
            logger.warning(f"top-skills-bar error: {e}")
            import plotly.graph_objects as go
            fig = go.Figure()
            fig.update_layout(
                title="⏳ Pipeline running, data loading...",
                template="plotly_white", height=450
            )
            return fig

    # ── Tab 1: Skill Category Pie ────────────────────────────────
    @app.callback(
        Output("skill-category-pie", "figure"),
        Input("stats-refresh-interval", "n_intervals")
    )
    def update_skill_category_pie(n):
        try:
            df = get_skill_category_breakdown()
            return build_skill_category_pie(df)
        except Exception as e:
            logger.warning(f"skill-category-pie error: {e}")
            import plotly.graph_objects as go
            fig = go.Figure()
            fig.update_layout(
                title="⏳ Pipeline running, data loading...",
                template="plotly_white", height=450
            )
            return fig

    # ── Tab 1: Job Title Keywords Bar ────────────────────────────
    @app.callback(
        Output("job-title-keywords-bar", "figure"),
        Input("job-title-dropdown", "value")
    )
    def update_job_title_keywords(selected_title):
        if not selected_title:
            df = pd.DataFrame(columns=["keyword", "frequency"])
            return build_job_title_keywords_bar(df, "Select a job title above")
        try:
            df = get_top_keywords_by_title(selected_title)
            return build_job_title_keywords_bar(df, selected_title)
        except Exception as e:
            logger.warning(f"job-title-keywords error: {e}")
            import plotly.graph_objects as go
            return go.Figure()

    # ── Tab 2: Keyword Treemap ───────────────────────────────────
    @app.callback(
        Output("keyword-treemap", "figure"),
        Input("stats-refresh-interval", "n_intervals")
    )
    def update_keyword_treemap(n):
        try:
            df = get_keyword_trends(limit=50)
            return build_keyword_treemap(df)
        except Exception as e:
            logger.warning(f"keyword-treemap error: {e}")
            import plotly.graph_objects as go
            fig = go.Figure()
            fig.update_layout(
                title="⏳ Pipeline running, data loading...",
                template="plotly_white", height=500
            )
            return fig

    # ── Tab 2: Keyword Table ─────────────────────────────────────
    @app.callback(
        Output("keyword-table", "children"),
        Input("stats-refresh-interval", "n_intervals")
    )
    def update_keyword_table(n):
        try:
            df = get_keyword_trends(limit=50)
            df.columns = ["Keyword", "Total Frequency"]
            df["Rank"] = range(1, len(df) + 1)
            df = df[["Rank", "Keyword", "Total Frequency"]]
            rows = []
            for _, row in df.iterrows():
                rows.append(html.Tr([
                    html.Td(int(row["Rank"]),
                            style={"fontWeight": "600", "color": "#4361ee"}),
                    html.Td(row["Keyword"].title()),
                    html.Td(int(row["Total Frequency"]))
                ]))
            return dbc.Table(
                [html.Thead(html.Tr([
                    html.Th("Rank"), html.Th("Keyword"), html.Th("Total Frequency")
                ]))] + [html.Tbody(rows)],
                striped=True, hover=True, responsive=True,
                style={"fontSize": "14px"}
            )
        except Exception:
            return html.P("⏳ Data loading, please wait...",
                          className="text-muted")

    # ── Tab 3: Topic Distribution ────────────────────────────────
    @app.callback(
        Output("topic-distribution-bar", "figure"),
        Input("stats-refresh-interval", "n_intervals")
    )
    def update_topic_distribution(n):
        try:
            df = get_topic_distribution()
            return build_topic_distribution_bar(df)
        except Exception as e:
            logger.warning(f"topic-distribution error: {e}")
            import plotly.graph_objects as go
            fig = go.Figure()
            fig.update_layout(
                title="⏳ Pipeline running, data loading...",
                template="plotly_white", height=450
            )
            return fig
