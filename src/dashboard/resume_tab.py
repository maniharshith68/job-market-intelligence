# src/dashboard/resume_tab.py

import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State
from src.llm.resume_scorer import score_resume
from src.utils.logger import get_logger

logger = get_logger("dashboard.resume_tab")

CARD_STYLE = {
    "borderRadius": "12px",
    "boxShadow": "0 2px 12px rgba(0,0,0,0.08)",
    "border": "none",
    "marginBottom": "24px"
}

SCORE_COLORS = {
    "Strong Match":  "#06d6a0",
    "Good Match":    "#4361ee",
    "Partial Match": "#f77f00",
    "Poor Match":    "#ef233c",
    "Unknown":       "#adb5bd"
}


def get_score_color(score: int) -> str:
    if score >= 75:
        return "#06d6a0"
    elif score >= 60:
        return "#4361ee"
    elif score >= 40:
        return "#f77f00"
    return "#ef233c"


def create_resume_tab_layout() -> dbc.Tab:
    return dbc.Tab(
        label="🤖 Resume Scorer",
        tab_style={"fontWeight": "500", "fontSize": "15px",
                   "padding": "12px 24px", "borderRadius": "8px 8px 0 0"},
        children=[
            html.Br(),

            # ── Instructions Banner ──────────────────────────────
            dbc.Alert([
                html.H6("🤖 AI-Powered Resume Fit Scorer", className="mb-1",
                        style={"fontWeight": "700"}),
                html.P("Paste your resume and a job description below. "
                       "Llama 3.3 70B will analyze your fit and provide "
                       "detailed feedback instantly.",
                       className="mb-0", style={"fontSize": "13px"})
            ], color="primary", style={"borderRadius": "12px"}),

            # ── Input Row ────────────────────────────────────────
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("📄 Your Resume",
                                    style={"fontWeight": "600",
                                           "marginBottom": "12px"}),
                            dcc.Textarea(
                                id="resume-input",
                                placeholder="Paste your full resume text here...",
                                style={
                                    "width": "100%",
                                    "height": "320px",
                                    "borderRadius": "8px",
                                    "border": "1px solid #dee2e6",
                                    "padding": "12px",
                                    "fontSize": "13px",
                                    "resize": "vertical",
                                    "fontFamily": "Inter, sans-serif"
                                }
                            )
                        ])
                    ], style=CARD_STYLE)
                ], md=6),

                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("💼 Job Description",
                                    style={"fontWeight": "600",
                                           "marginBottom": "12px"}),
                            dcc.Textarea(
                                id="job-desc-input",
                                placeholder="Paste the job description here...",
                                style={
                                    "width": "100%",
                                    "height": "320px",
                                    "borderRadius": "8px",
                                    "border": "1px solid #dee2e6",
                                    "padding": "12px",
                                    "fontSize": "13px",
                                    "resize": "vertical",
                                    "fontFamily": "Inter, sans-serif"
                                }
                            )
                        ])
                    ], style=CARD_STYLE)
                ], md=6)
            ]),

            # ── Score Button ─────────────────────────────────────
            dbc.Row([
                dbc.Col([
                    dbc.Button(
                        "🚀 Score My Resume",
                        id="score-btn",
                        color="primary",
                        size="lg",
                        style={
                            "width": "100%",
                            "borderRadius": "10px",
                            "fontWeight": "600",
                            "fontSize": "16px",
                            "padding": "14px"
                        }
                    )
                ], md=6, className="mx-auto")
            ], className="mb-4"),

            # ── Loading + Results ────────────────────────────────
            dbc.Row([
                dbc.Col([
                    dcc.Loading(
                        id="scoring-loading",
                        type="circle",
                        color="#4361ee",
                        children=[html.Div(id="score-results")]
                    )
                ], md=12)
            ])
        ]
    )


def build_score_results(result: dict) -> html.Div:
    """Build the score results UI from the LLM response dict."""
    score = result.get("fit_score", 0)
    recommendation = result.get("recommendation", "Unknown")
    experience = result.get("experience_match", "Unknown")
    matched = result.get("matched_skills", [])
    missing = result.get("missing_skills", [])
    strengths = result.get("strengths", "")
    suggestions = result.get("suggestions", "")

    score_color = get_score_color(score)
    rec_color = SCORE_COLORS.get(recommendation, "#adb5bd")

    return html.Div([

        # ── Score Header Card ────────────────────────────────────
        dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.H1(f"{score}",
                                    style={"fontSize": "72px",
                                           "fontWeight": "800",
                                           "color": score_color,
                                           "lineHeight": "1"}),
                            html.P("/ 100", style={"color": "#adb5bd",
                                                   "fontSize": "20px",
                                                   "marginTop": "-8px"}),
                            html.P("Fit Score", style={"fontWeight": "600",
                                                       "color": "#2d3436"})
                        ], style={"textAlign": "center"})
                    ], md=3),

                    dbc.Col([
                        html.Div([
                            dbc.Badge(recommendation,
                                      style={"backgroundColor": rec_color,
                                             "fontSize": "14px",
                                             "padding": "8px 16px",
                                             "borderRadius": "20px",
                                             "marginBottom": "8px"}),
                            html.Br(),
                            dbc.Badge(experience,
                                      color="secondary",
                                      style={"fontSize": "13px",
                                             "padding": "6px 14px",
                                             "borderRadius": "20px"})
                        ], style={"paddingTop": "16px"})
                    ], md=3),

                    dbc.Col([
                        html.P("💪 Strengths", style={"fontWeight": "700",
                                                       "marginBottom": "6px"}),
                        html.P(strengths, style={"fontSize": "13px",
                                                  "color": "#636e72",
                                                  "lineHeight": "1.6"})
                    ], md=6)
                ])
            ])
        ], style={**CARD_STYLE, "borderLeft": f"5px solid {score_color}"}),

        # ── Skills Row ───────────────────────────────────────────
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("✅ Matched Skills",
                                style={"fontWeight": "600",
                                       "color": "#06d6a0",
                                       "marginBottom": "12px"}),
                        html.Div([
                            dbc.Badge(skill,
                                      style={"backgroundColor": "#06d6a0",
                                             "marginRight": "6px",
                                             "marginBottom": "6px",
                                             "fontSize": "12px",
                                             "padding": "6px 12px",
                                             "borderRadius": "16px"})
                            for skill in matched
                        ]) if matched else html.P("No matched skills found.",
                                                   className="text-muted")
                    ])
                ], style=CARD_STYLE)
            ], md=6),

            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("❌ Missing Skills",
                                style={"fontWeight": "600",
                                       "color": "#ef233c",
                                       "marginBottom": "12px"}),
                        html.Div([
                            dbc.Badge(skill,
                                      style={"backgroundColor": "#ef233c",
                                             "marginRight": "6px",
                                             "marginBottom": "6px",
                                             "fontSize": "12px",
                                             "padding": "6px 12px",
                                             "borderRadius": "16px"})
                            for skill in missing
                        ]) if missing else html.P("No major gaps found! 🎉",
                                                   className="text-muted")
                    ])
                ], style=CARD_STYLE)
            ], md=6)
        ]),

        # ── Suggestions Card ─────────────────────────────────────
        dbc.Card([
            dbc.CardBody([
                html.H5("💡 Actionable Suggestions",
                        style={"fontWeight": "600", "marginBottom": "12px"}),
                html.P(suggestions, style={"fontSize": "14px",
                                            "color": "#636e72",
                                            "lineHeight": "1.8"})
            ])
        ], style={**CARD_STYLE, "borderLeft": "5px solid #4361ee"})
    ])


def register_resume_callbacks(app):

    @app.callback(
        Output("score-results", "children"),
        Input("score-btn", "n_clicks"),
        State("resume-input", "value"),
        State("job-desc-input", "value"),
        prevent_initial_call=True
    )
    def run_resume_scorer(n_clicks, resume_text, job_desc_text):
        if not resume_text or not resume_text.strip():
            return dbc.Alert("⚠️ Please paste your resume text.",
                             color="warning", style={"borderRadius": "10px"})
        if not job_desc_text or not job_desc_text.strip():
            return dbc.Alert("⚠️ Please paste a job description.",
                             color="warning", style={"borderRadius": "10px"})

        try:
            logger.info("Resume scoring triggered from dashboard")
            result = score_resume(resume_text, job_desc_text)
            return build_score_results(result)
        except Exception as e:
            logger.error(f"Resume scoring failed: {e}")
            return dbc.Alert(
                f"❌ Scoring failed: {str(e)}",
                color="danger",
                style={"borderRadius": "10px"}
            )
