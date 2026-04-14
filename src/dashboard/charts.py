# src/dashboard/charts.py

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

COLOR_PALETTE = px.colors.qualitative.Bold
TEMPLATE = "plotly_white"


def build_top_skills_bar(df: pd.DataFrame) -> go.Figure:
    """Horizontal bar chart of top 10 skills by frequency."""
    df = df[df["skill"].str.len() > 1].copy()
    df = df.sort_values("frequency", ascending=True)

    color_map = {
        "programming_languages": "#4361ee",
        "cloud_and_devops":      "#f72585",
        "databases":             "#7209b7",
        "data_and_ml":           "#3a0ca3",
        "soft_skills":           "#4cc9f0",
        "web_frameworks":        "#f77f00",
        "tools_and_platforms":   "#06d6a0",
        "data_visualization":    "#118ab2",
        "business_and_domain":   "#ef233c",
        "other":                 "#adb5bd"
    }

    colors = df["category"].map(color_map).fillna("#adb5bd").tolist()

    fig = go.Figure(go.Bar(
        x=df["frequency"],
        y=df["skill"].str.title(),
        orientation="h",
        marker_color=colors,
        text=df["frequency"],
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Frequency: %{x}<extra></extra>"
    ))

    fig.update_layout(
        title={
            "text": "🔥 Top In-Demand Skills",
            "font": {"size": 20, "color": "#2d3436"}
        },
        xaxis_title="Number of Job Postings",
        yaxis_title="",
        template=TEMPLATE,
        height=450,
        margin=dict(l=20, r=60, t=60, b=40),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )
    return fig


def build_skill_category_pie(df: pd.DataFrame) -> go.Figure:
    """Pie chart of skill frequency by category."""
    labels = df["category"].str.replace("_", " ").str.title()

    fig = go.Figure(go.Pie(
        labels=labels,
        values=df["total_frequency"],
        hole=0.4,
        marker=dict(colors=COLOR_PALETTE),
        hovertemplate="<b>%{label}</b><br>Total: %{value}<br>%{percent}<extra></extra>"
    ))

    fig.update_layout(
        title={
            "text": "📊 Skill Category Breakdown",
            "font": {"size": 20, "color": "#2d3436"}
        },
        template=TEMPLATE,
        height=450,
        margin=dict(l=20, r=20, t=60, b=20),
        legend=dict(orientation="v", x=1.05),
        paper_bgcolor="rgba(0,0,0,0)"
    )
    return fig


def build_keyword_treemap(df: pd.DataFrame) -> go.Figure:
    """Treemap of top keywords by total frequency."""
    df = df[df["keyword"].str.len() > 2].head(40)

    fig = px.treemap(
        df,
        path=["keyword"],
        values="total_frequency",
        color="total_frequency",
        color_continuous_scale="Blues",
        hover_data={"total_frequency": True}
    )

    fig.update_traces(
        textinfo="label+value",
        hovertemplate="<b>%{label}</b><br>Frequency: %{value}<extra></extra>"
    )

    fig.update_layout(
        title={
            "text": "🗺️ Keyword Frequency Treemap",
            "font": {"size": 20, "color": "#2d3436"}
        },
        template=TEMPLATE,
        height=500,
        margin=dict(l=10, r=10, t=60, b=10),
        paper_bgcolor="rgba(0,0,0,0)"
    )
    return fig


def build_topic_distribution_bar(df: pd.DataFrame) -> go.Figure:
    """Bar chart of BERTopic topic sizes."""
    fig = go.Figure(go.Bar(
        x=df["topic_label"],
        y=df["job_count"],
        marker_color=COLOR_PALETTE[:len(df)],
        text=df["job_count"],
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Jobs: %{y}<extra></extra>"
    ))

    fig.update_layout(
        title={
            "text": "🧠 BERTopic — Jobs per Topic Cluster",
            "font": {"size": 20, "color": "#2d3436"}
        },
        xaxis_title="Topic",
        yaxis_title="Number of Jobs",
        template=TEMPLATE,
        height=450,
        margin=dict(l=20, r=20, t=60, b=60),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )
    return fig


def build_job_title_keywords_bar(df: pd.DataFrame, title: str) -> go.Figure:
    """Horizontal bar chart of top keywords for a selected job title."""
    if df.empty:
        fig = go.Figure()
        fig.update_layout(
            title="No data found for selected job title",
            template=TEMPLATE,
            height=350
        )
        return fig

    df = df.sort_values("frequency", ascending=True)

    fig = go.Figure(go.Bar(
        x=df["frequency"],
        y=df["keyword"],
        orientation="h",
        marker_color="#4361ee",
        text=df["frequency"],
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Frequency: %{x}<extra></extra>"
    ))

    fig.update_layout(
        title={
            "text": f"🔍 Top Keywords — {title}",
            "font": {"size": 18, "color": "#2d3436"}
        },
        xaxis_title="Frequency",
        yaxis_title="",
        template=TEMPLATE,
        height=380,
        margin=dict(l=20, r=60, t=60, b=40),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )
    return fig
