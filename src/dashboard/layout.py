# src/dashboard/layout.py

import dash_bootstrap_components as dbc
from dash import dcc, html
from src.dashboard.resume_tab import create_resume_tab_layout
from dash import dcc


HEADER_STYLE = {
    "background": "linear-gradient(135deg, #2d3436 0%, #4361ee 100%)",
    "padding": "24px 32px",
    "marginBottom": "0px"
}

CARD_STYLE = {
    "borderRadius": "12px",
    "boxShadow": "0 2px 12px rgba(0,0,0,0.08)",
    "border": "none",
    "marginBottom": "24px"
}

TAB_STYLE = {
    "fontWeight": "500",
    "fontSize": "15px",
    "padding": "12px 24px",
    "borderRadius": "8px 8px 0 0"
}


def create_stat_card(title: str, value: str, icon: str, color: str) -> dbc.Card:
    return dbc.Card([
        dbc.CardBody([
            html.Div([
                html.Span(icon, style={"fontSize": "28px"}),
                html.Div([
                    html.H4(value, className="mb-0",
                            style={"color": color, "fontWeight": "700"}),
                    html.P(title, className="mb-0 text-muted",
                           style={"fontSize": "13px"})
                ], style={"marginLeft": "12px"})
            ], style={"display": "flex", "alignItems": "center"})
        ])
    ], style=CARD_STYLE)


def create_layout(total_jobs: int) -> html.Div:
    return html.Div([

        # ── Header ──────────────────────────────────────────────
        html.Div([
            # Add pipeline status refresh interval
            dcc.Interval(
                id="pipeline-check-interval",
                interval=10000,  # check every 10 seconds
                n_intervals=0
            ),
            dbc.Container([
                dbc.Row([
                    dbc.Col([
                        html.H2("🧠 Job Market Intelligence Platform",
                                style={"color": "white", "fontWeight": "700",
                                       "marginBottom": "4px"}),
                        html.P("Real-Time Skill Trend Dashboard • NLP-Powered Analytics",
                               style={"color": "rgba(255,255,255,0.75)",
                                      "marginBottom": "0", "fontSize": "14px"})
                    ])
                ])
            ], fluid=True)
        ], style=HEADER_STYLE),

        # ── Main Content ────────────────────────────────────────
        dbc.Container([

            html.Br(),

            # ── Stat Cards ──────────────────────────────────────
            dbc.Row([
                dbc.Col(create_stat_card(
                    "Total Jobs Analyzed", str(total_jobs), "📋", "#4361ee"), md=3),
                dbc.Col(create_stat_card(
                    "Unique Skills Found", "505", "🔧", "#f72585"), md=3),
                dbc.Col(create_stat_card(
                    "Topic Clusters", "63", "🧠", "#7209b7"), md=3),
                dbc.Col(create_stat_card(
                    "Keyword Trends", "8,390", "📈", "#4cc9f0"), md=3),
            ], className="mb-2"),

            # ── Tabs ────────────────────────────────────────────
            dbc.Tabs([

                # ── Tab 1: Skill Intelligence ────────────────────
                dbc.Tab(label="🔥 Skill Intelligence", tab_style=TAB_STYLE, children=[
                    html.Br(),
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    dcc.Graph(id="top-skills-bar")
                                ])
                            ], style=CARD_STYLE)
                        ], md=7),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    dcc.Graph(id="skill-category-pie")
                                ])
                            ], style=CARD_STYLE)
                        ], md=5),
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.H5("🔍 Explore Keywords by Job Title",
                                            className="mb-3",
                                            style={"fontWeight": "600"}),
                                    dcc.Dropdown(
                                        id="job-title-dropdown",
                                        placeholder="Select a job title...",
                                        clearable=True,
                                        style={"marginBottom": "16px"}
                                    ),
                                    dcc.Graph(id="job-title-keywords-bar")
                                ])
                            ], style=CARD_STYLE)
                        ], md=12)
                    ])
                ]),

                # ── Tab 2: Keyword Trends ────────────────────────
                dbc.Tab(label="📈 Keyword Trends", tab_style=TAB_STYLE, children=[
                    html.Br(),
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    dcc.Graph(id="keyword-treemap")
                                ])
                            ], style=CARD_STYLE)
                        ], md=12)
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.H5("📋 Top 50 Keywords Table",
                                            className="mb-3",
                                            style={"fontWeight": "600"}),
                                    html.Div(id="keyword-table")
                                ])
                            ], style=CARD_STYLE)
                        ], md=12)
                    ])
                ]),

                # ── Tab 3: Topic Explorer ────────────────────────
                dbc.Tab(label="🧠 Topic Explorer", tab_style=TAB_STYLE, children=[
                    html.Br(),
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    dcc.Graph(id="topic-distribution-bar")
                                ])
                            ], style=CARD_STYLE)
                        ], md=12)
                    ])
                ]),

                # ── Tab 4: Resume Tab ────────────────────────
                dbc.Tab(label="📄 Resume Insights", tab_style=TAB_STYLE, children=[
                    html.Br(),
                    create_resume_tab_layout()
                ]),

            ], style={"marginTop": "8px"}),

            html.Footer([
                html.Hr(),
                html.P("Job Market Intelligence Platform • Built with Plotly Dash + PostgreSQL + BERTopic",
                       className="text-center text-muted",
                       style={"fontSize": "12px"})
            ])

        ], fluid=True)
    ])
