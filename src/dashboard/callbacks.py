# src/dashboard/callbacks.py

import pandas as pd
from dash import Input, Output
import dash_bootstrap_components as dbc
from dash import html
import plotly.graph_objects as go
import os
import sys

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

LOADING_FIGURE = go.Figure()
LOADING_FIGURE.update_layout(
    title="⏳ Data loading, please wait...",
    template="plotly_white",
    height=450,
    annotations=[{
        "text": "Pipeline is running in background.<br>Charts will load automatically.",
        "xref": "paper", "yref": "paper",
        "x": 0.5, "y": 0.5,
        "xanchor": "center", "yanchor": "middle",
        "showarrow": False,
        "font": {"size": 14, "color": "#636e72"}
    }]
)


def safe_figure(build_fn, *args, fallback_title="⏳ Data loading..."):
    """Safely call a chart builder, return loading figure on any error."""
    try:
        return build_fn(*args)
    except Exception as e:
        logger.warning(f"{fallback_title} error: {str(e)[:120]}")
        fig = go.Figure()
        fig.update_layout(
            title=fallback_title,
            template="plotly_white",
            height=450
        )
        return fig


def register_callbacks(app):

    # ── Auto-refresh status check ────────────────────────────────
    @app.callback(
        Output("stats-refresh-output", "children"),
        Input("stats-refresh-interval", "n_intervals")
    )
    def refresh_pipeline_status(n):
        try:
            count = get_total_job_count()
            if count and count > 0:
                logger.info(f"DB status: {count} jobs available")
        except Exception as e:
            logger.warning(f"Status check failed: {str(e)[:80]}")
        return ""

    # ── Job title dropdown ───────────────────────────────────────
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

    # ── Top Skills Bar ───────────────────────────────────────────
    @app.callback(
        Output("top-skills-bar", "figure"),
        Input("stats-refresh-interval", "n_intervals")
    )
    def update_top_skills_bar(n):
        return safe_figure(
            lambda: build_top_skills_bar(get_top_skills()),
            fallback_title="⏳ Skills loading..."
        )

    # ── Skill Category Pie ───────────────────────────────────────
    @app.callback(
        Output("skill-category-pie", "figure"),
        Input("stats-refresh-interval", "n_intervals")
    )
    def update_skill_category_pie(n):
        return safe_figure(
            lambda: build_skill_category_pie(get_skill_category_breakdown()),
            fallback_title="⏳ Categories loading..."
        )

    # ── Job Title Keywords Bar ───────────────────────────────────
    @app.callback(
        Output("job-title-keywords-bar", "figure"),
        Input("job-title-dropdown", "value")
    )
    def update_job_title_keywords(selected_title):
        if not selected_title:
            df = pd.DataFrame(columns=["keyword", "frequency"])
            return build_job_title_keywords_bar(df, "Select a job title above")
        return safe_figure(
            lambda: build_job_title_keywords_bar(
                get_top_keywords_by_title(selected_title), selected_title
            ),
            fallback_title="⏳ Loading keywords..."
        )

    # ── Keyword Treemap ──────────────────────────────────────────
    @app.callback(
        Output("keyword-treemap", "figure"),
        Input("stats-refresh-interval", "n_intervals")
    )
    def update_keyword_treemap(n):
        return safe_figure(
            lambda: build_keyword_treemap(get_keyword_trends(limit=50)),
            fallback_title="⏳ Keywords loading..."
        )

    # ── Keyword Table ────────────────────────────────────────────
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
            rows = [
                html.Tr([
                    html.Td(int(row["Rank"]),
                            style={"fontWeight": "600", "color": "#4361ee"}),
                    html.Td(row["Keyword"].title()),
                    html.Td(int(row["Total Frequency"]))
                ])
                for _, row in df.iterrows()
            ]
            return dbc.Table(
                [html.Thead(html.Tr([
                    html.Th("Rank"),
                    html.Th("Keyword"),
                    html.Th("Total Frequency")
                ]))] + [html.Tbody(rows)],
                striped=True, hover=True, responsive=True,
                style={"fontSize": "14px"}
            )
        except Exception:
            return html.P("⏳ Data loading, please wait...",
                          className="text-muted")

    # ── Topic Distribution ───────────────────────────────────────
    @app.callback(
        Output("topic-distribution-bar", "figure"),
        Input("stats-refresh-interval", "n_intervals")
    )
    def update_topic_distribution(n):
        return safe_figure(
            lambda: build_topic_distribution_bar(get_topic_distribution()),
            fallback_title="⏳ Topics loading..."
        )
