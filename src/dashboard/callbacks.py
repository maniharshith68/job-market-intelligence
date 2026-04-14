# src/dashboard/callbacks.py

import pandas as pd
from dash import Input, Output, callback
import dash_bootstrap_components as dbc
from dash import html

from src.dashboard.data_loader import (
    get_top_skills,
    get_keyword_trends,
    get_topic_distribution,
    get_skill_category_breakdown,
    get_top_keywords_by_title,
    get_all_job_titles
)
from src.dashboard.charts import (
    build_top_skills_bar,
    build_skill_category_pie,
    build_keyword_treemap,
    build_topic_distribution_bar,
    build_job_title_keywords_bar
)


def register_callbacks(app):

    # ── Populate job title dropdown on load ─────────────────────
    @app.callback(
        Output("job-title-dropdown", "options"),
        Input("job-title-dropdown", "search_value")
    )
    def load_job_titles(search_value):
        titles = get_all_job_titles()
        if search_value:
            titles = [t for t in titles if search_value.lower() in t.lower()]
        return [{"label": t, "value": t} for t in titles[:100]]

    # ── Tab 1: Top Skills Bar ────────────────────────────────────
    @app.callback(
        Output("top-skills-bar", "figure"),
        Input("job-title-dropdown", "value")
    )
    def update_top_skills_bar(_):
        df = get_top_skills()
        return build_top_skills_bar(df)

    # ── Tab 1: Skill Category Pie ────────────────────────────────
    @app.callback(
        Output("skill-category-pie", "figure"),
        Input("job-title-dropdown", "value")
    )
    def update_skill_category_pie(_):
        df = get_skill_category_breakdown()
        return build_skill_category_pie(df)

    # ── Tab 1: Job Title Keywords Bar ────────────────────────────
    @app.callback(
        Output("job-title-keywords-bar", "figure"),
        Input("job-title-dropdown", "value")
    )
    def update_job_title_keywords(selected_title):
        if not selected_title:
            df = pd.DataFrame(columns=["keyword", "frequency"])
            return build_job_title_keywords_bar(df, "Select a job title above")
        df = get_top_keywords_by_title(selected_title)
        return build_job_title_keywords_bar(df, selected_title)

    # ── Tab 2: Keyword Treemap ───────────────────────────────────
    @app.callback(
        Output("keyword-treemap", "figure"),
        Input("job-title-dropdown", "value")
    )
    def update_keyword_treemap(_):
        df = get_keyword_trends(limit=50)
        return build_keyword_treemap(df)

    # ── Tab 2: Keyword Table ─────────────────────────────────────
    @app.callback(
        Output("keyword-table", "children"),
        Input("job-title-dropdown", "value")
    )
    def update_keyword_table(_):
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

        table = dbc.Table(
            [html.Thead(html.Tr([
                html.Th("Rank"), html.Th("Keyword"), html.Th("Total Frequency")
            ]))] + [html.Tbody(rows)],
            striped=True, hover=True, responsive=True,
            style={"fontSize": "14px"}
        )
        return table

    # ── Tab 3: Topic Distribution ────────────────────────────────
    @app.callback(
        Output("topic-distribution-bar", "figure"),
        Input("job-title-dropdown", "value")
    )
    def update_topic_distribution(_):
        df = get_topic_distribution()
        return build_topic_distribution_bar(df)
