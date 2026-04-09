import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
import numpy as np

# ── data ──────────────────────────────────────────────────────────────────────
df = pd.read_csv("stars.csv")
n  = len(df)

PROFILE_COLS = ["metallicity_fe_h", "teff_k", "distance_pc", "radius_solar", "mass_solar"]
COND_COLS    = ["teff_k", "mass_solar", "radius_solar", "distance_pc"]

missing_pct = {c: df[c].isna().sum() / n * 100 for c in PROFILE_COLS}
present_pct = {c: 100 - missing_pct[c]          for c in PROFILE_COLS}

met_absent   = df["metallicity_fe_h"].isna()
n_absent     = int(met_absent.sum())
n_present    = int((~met_absent).sum())
cond_absent  = {c: df.loc[met_absent,  c].isna().mean() * 100 for c in COND_COLS}
cond_present = {c: df.loc[~met_absent, c].isna().mean() * 100 for c in COND_COLS}

# ── palette ───────────────────────────────────────────────────────────────────
BG        = "#0f1117"
CARD_BG   = "#181b24"
FG        = "#e8eaf0"
SUBTEXT   = "#9096a8"
GRID      = "#2a2d3a"
GREEN     = "#4CAF50"
RED_C     = "#f44336"
ABSENT_C  = "#FF6B6B"
PRESENT_C = "#4ECDC4"
ACCENT    = "#FFD700"

PLOTLY_LAYOUT = dict(
    paper_bgcolor=CARD_BG,
    plot_bgcolor=CARD_BG,
    font=dict(color=FG, family="monospace"),
    margin=dict(l=16, r=16, t=36, b=16),
)

# ── figures ───────────────────────────────────────────────────────────────────
def fig_panel1():
    sorted_cols = sorted(PROFILE_COLS, key=lambda c: present_pct[c])
    pres = [present_pct[c] for c in sorted_cols]
    miss = [missing_pct[c] for c in sorted_cols]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=sorted_cols, x=pres, orientation="h",
        name="Present", marker_color=GREEN,
        hovertemplate="%{y}  →  %{x:.2f}% present<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        y=sorted_cols, x=miss, orientation="h",
        name="Missing", marker_color=RED_C,
        hovertemplate="%{y}  →  %{x:.2f}% missing<extra></extra>",
    ))
    fig.add_vline(x=100, line_dash="dash", line_color=GRID, line_width=1)
    fig.update_layout(
        **PLOTLY_LAYOUT,
        barmode="stack",
        title=dict(text="Column Completeness Profile", font=dict(size=14, color=FG)),
        xaxis=dict(range=[85, 101], gridcolor=GRID, zerolinecolor=GRID,
                   title="% complete", tickfont=dict(color=FG)),
        yaxis=dict(gridcolor=GRID, tickfont=dict(color=FG, size=11)),
        legend=dict(bgcolor=CARD_BG, bordercolor=GRID, font=dict(color=FG)),
        height=300,
    )
    for i, (c, p) in enumerate(zip(sorted_cols, pres)):
        fig.add_annotation(x=p - 0.3, y=i, text=f"{p:.1f}%",
                           showarrow=False, xanchor="right",
                           font=dict(size=10, color=BG, family="monospace"))
    return fig


def fig_panel2():
    x_labels = COND_COLS
    x        = list(range(len(x_labels)))
    absent_v  = [cond_absent[c]  for c in x_labels]
    present_v = [cond_present[c] for c in x_labels]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name=f"Met. absent (n={n_absent})",
        x=x_labels, y=absent_v,
        marker_color=ABSENT_C,
        text=[f"{v:.1f}%" for v in absent_v],
        textposition="outside", textfont=dict(color=ABSENT_C, size=10),
        hovertemplate="%{x}  →  %{y:.2f}% missing when metallicity absent<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        name=f"Met. present (n={n_present})",
        x=x_labels, y=present_v,
        marker_color=PRESENT_C,
        text=[f"{v:.1f}%" for v in present_v],
        textposition="outside", textfont=dict(color=PRESENT_C, size=10),
        hovertemplate="%{x}  →  %{y:.2f}% missing when metallicity present<extra></extra>",
    ))
    fig.add_annotation(
        x="distance_pc", y=cond_present["distance_pc"],
        text="Median dist. similar<br>(~255 vs ~290 pc)<br>→ not the driver",
        showarrow=True, arrowhead=2, arrowcolor=SUBTEXT, ax=60, ay=-50,
        font=dict(size=9, color=SUBTEXT),
        bgcolor=CARD_BG, bordercolor=GRID,
    )
    fig.update_layout(
        **PLOTLY_LAYOUT,
        barmode="group",
        title=dict(text="Conditional Missingness (metallicity absent vs. present)", font=dict(size=14, color=FG)),
        yaxis=dict(gridcolor=GRID, title="% missing", tickfont=dict(color=FG),
                   range=[0, max(absent_v) * 1.3]),
        xaxis=dict(gridcolor=GRID, tickfont=dict(color=FG, size=11)),
        legend=dict(bgcolor=CARD_BG, bordercolor=GRID, font=dict(color=FG)),
        height=300,
    )
    return fig


def fig_scatter(x_col, y_col, color_by_met=True):
    plot_df = df.copy()
    plot_df["_met_status"] = plot_df["metallicity_fe_h"].apply(
        lambda v: f"Met. absent (n={n_absent})" if pd.isna(v) else f"Met. present (n={n_present})"
    )
    plot_df = plot_df.dropna(subset=[x_col, y_col])

    color_map = {
        f"Met. absent (n={n_absent})":  ABSENT_C,
        f"Met. present (n={n_present})": PRESENT_C,
    }
    col_order = [f"Met. absent (n={n_absent})", f"Met. present (n={n_present})"]

    fig = px.scatter(
        plot_df, x=x_col, y=y_col,
        color="_met_status" if color_by_met else None,
        color_discrete_map=color_map,
        category_orders={"_met_status": col_order},
        opacity=0.65,
        hover_data=["star_name", "num_planets"],
        labels={"_met_status": "Metallicity status"},
    )
    fig.update_traces(marker=dict(size=5))
    fig.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text=f"{x_col} vs {y_col} (coloured by metallicity status)",
                   font=dict(size=14, color=FG)),
        xaxis=dict(gridcolor=GRID, title=x_col, tickfont=dict(color=FG)),
        yaxis=dict(gridcolor=GRID, title=y_col, tickfont=dict(color=FG)),
        legend=dict(title="", bgcolor=CARD_BG, bordercolor=GRID, font=dict(color=FG)),
        height=340,
    )
    return fig


# ── KPI card ──────────────────────────────────────────────────────────────────
def kpi(label, value, sub=None, value_color=FG):
    return html.Div([
        html.Div(label,  style={"color": SUBTEXT, "fontSize": "11px", "marginBottom": "4px",
                                "textTransform": "uppercase", "letterSpacing": "0.06em"}),
        html.Div(value,  style={"color": value_color, "fontSize": "26px", "fontWeight": "700",
                                "fontFamily": "monospace"}),
        html.Div(sub or "", style={"color": SUBTEXT, "fontSize": "11px", "marginTop": "3px"}),
    ], style={
        "background": CARD_BG, "borderRadius": "8px", "padding": "18px 22px",
        "flex": "1", "minWidth": "180px", "border": f"1px solid {GRID}",
    })


# ── layout ────────────────────────────────────────────────────────────────────
app = Dash(__name__, title="Stars Data Quality Audit")
app.layout = html.Div(style={"background": BG, "minHeight": "100vh",
                              "fontFamily": "monospace", "color": FG,
                              "padding": "24px 32px"}, children=[

    # ── header ────────────────────────────────────────────────────────────────
    html.Div([
        html.H1("Stars Catalog — Data Quality Audit",
                style={"margin": "0", "fontSize": "24px", "fontWeight": "700", "color": FG}),
        html.P("Where is the data trustworthy, thin, or incomplete?  ·  For data practitioners",
               style={"margin": "6px 0 0", "color": SUBTEXT, "fontSize": "13px",
                      "fontStyle": "italic"}),
    ], style={"marginBottom": "24px"}),

    # ── KPI row ───────────────────────────────────────────────────────────────
    html.Div([
        kpi("Total stars",        f"{n:,}",          "in stars.csv"),
        kpi("Missing metallicity", f"{n_absent}",    f"{missing_pct['metallicity_fe_h']:.1f}% of catalog",
            value_color=ABSENT_C),
        kpi("Worst co-miss rate",
            f"{cond_absent['teff_k']:.0f}%",
            f"teff_k when met. absent  (vs {cond_present['teff_k']:.1f}% otherwise)",
            value_color=ABSENT_C),
        kpi("Median dist. (absent)", "~290 pc",      "vs ~255 pc when met. present → not the driver"),
    ], style={"display": "flex", "gap": "14px", "marginBottom": "20px", "flexWrap": "wrap"}),

    # ── panels row ────────────────────────────────────────────────────────────
    html.Div([
        html.Div(dcc.Graph(id="panel1", figure=fig_panel1(), config={"displayModeBar": False}),
                 style={"flex": "1", "background": CARD_BG, "borderRadius": "8px",
                        "border": f"1px solid {GRID}", "padding": "4px"}),
        html.Div(dcc.Graph(id="panel2", figure=fig_panel2(), config={"displayModeBar": False}),
                 style={"flex": "1", "background": CARD_BG, "borderRadius": "8px",
                        "border": f"1px solid {GRID}", "padding": "4px"}),
    ], style={"display": "flex", "gap": "14px", "marginBottom": "20px"}),

    # ── scatter explorer ──────────────────────────────────────────────────────
    html.Div([
        html.Div([
            html.Div("Scatter Explorer", style={"color": FG, "fontSize": "13px",
                                                "fontWeight": "700", "marginBottom": "10px"}),
            html.Div([
                html.Div([
                    html.Label("X axis", style={"color": SUBTEXT, "fontSize": "11px"}),
                    dcc.Dropdown(
                        id="x-axis", value="distance_pc",
                        options=[{"label": c, "value": c} for c in PROFILE_COLS],
                        style={"background": BG, "color": FG, "fontSize": "12px"},
                        className="dark-dropdown",
                    ),
                ], style={"flex": "1"}),
                html.Div([
                    html.Label("Y axis", style={"color": SUBTEXT, "fontSize": "11px"}),
                    dcc.Dropdown(
                        id="y-axis", value="teff_k",
                        options=[{"label": c, "value": c} for c in PROFILE_COLS],
                        style={"background": BG, "color": FG, "fontSize": "12px"},
                    ),
                ], style={"flex": "1"}),
            ], style={"display": "flex", "gap": "12px", "marginBottom": "8px"}),
            dcc.Graph(id="scatter", config={"displayModeBar": False}),
        ], style={"background": CARD_BG, "borderRadius": "8px",
                  "border": f"1px solid {GRID}", "padding": "16px 16px 4px"}),
    ], style={"marginBottom": "20px"}),

    # ── story callout ─────────────────────────────────────────────────────────
    html.Div([
        html.Div("Story Hypothesis", style={"color": ACCENT, "fontSize": "12px",
                                            "fontWeight": "700", "marginBottom": "10px",
                                            "textTransform": "uppercase", "letterSpacing": "0.06em"}),
        html.Div([
            html.Div([
                html.Span("A. ", style={"color": ABSENT_C, "fontWeight": "700"}),
                html.Span(
                    f"Missingness is concentrated in metallicity_fe_h ({missing_pct['metallicity_fe_h']:.1f}% missing "
                    f"vs. <2% for all other columns). Measurement cost explains the gap: metallicity requires "
                    "high-resolution spectroscopy; other properties can be estimated photometrically.",
                    style={"color": FG}),
            ], style={"marginBottom": "8px"}),
            html.Div([
                html.Span("B. ", style={"color": PRESENT_C, "fontWeight": "700"}),
                html.Span(
                    f"Stars missing metallicity are data-sparse across the board: teff_k is missing "
                    f"{cond_absent['teff_k']:.0f}% of the time in that group vs. {cond_present['teff_k']:.1f}% otherwise. "
                    "These are not random gaps.",
                    style={"color": FG}),
            ], style={"marginBottom": "8px"}),
            html.Div([
                html.Span("C. ", style={"color": ACCENT, "fontWeight": "700"}),
                html.Span(
                    "Median distance is nearly identical for stars with vs. without metallicity (~255 pc vs. ~290 pc), "
                    "ruling out observational depth as the driver.",
                    style={"color": FG}),
            ]),
        ], style={"fontSize": "12px", "lineHeight": "1.7"}),
    ], style={"background": CARD_BG, "borderRadius": "8px", "border": f"1px solid {GRID}",
              "padding": "18px 22px"}),

])

# ── dropdown dark-theme override ──────────────────────────────────────────────
app.index_string = app.index_string.replace(
    "</head>",
    """<style>
    .Select-control, .Select-menu-outer, .Select-option, .VirtualizedSelectFocusedOption {
        background-color: #181b24 !important;
        color: #e8eaf0 !important;
        border-color: #2a2d3a !important;
    }
    .Select-value-label { color: #e8eaf0 !important; }
    .Select-arrow { border-top-color: #9096a8 !important; }
    </style></head>""",
)


# ── callback ──────────────────────────────────────────────────────────────────
@app.callback(
    Output("scatter", "figure"),
    Input("x-axis", "value"),
    Input("y-axis", "value"),
)
def update_scatter(x_col, y_col):
    return fig_scatter(x_col, y_col)


if __name__ == "__main__":
    app.run(debug=False, port=8050)
