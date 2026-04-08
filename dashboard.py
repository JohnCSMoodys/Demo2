"""
Plotly Dash dashboard — Exoplanet Data Quality Audit
Run: python3 dashboard.py  →  http://127.0.0.1:8050
"""

import dash
from dash import dcc, html
import plotly.graph_objects as go
import data_prep

# ── Data ──────────────────────────────────────────────────────────────────────
_d = data_prep.load()
df                   = _d["df"]
n                    = _d["n"]
missing_pct          = _d["missing_pct"]
present_pct          = _d["present_pct"]
eqt_missing          = _d["eqt_missing"]
eqt_computed         = _d["eqt_computed"]
eqt_measured         = _d["eqt_measured"]
valid_years          = _d["valid_years"]
completeness_by_year = _d["completeness_by_year"]

profile_cols = data_prep.PROFILE_COLS
watch_cols   = data_prep.WATCH_COLS
sorted_cols  = sorted(profile_cols, key=lambda c: present_pct[c])

# ── Palette ───────────────────────────────────────────────────────────────────
DARK_BG  = "#0f1117"
PANEL_BG = "#1a1d27"
GREEN    = "#4ade80"
YELLOW   = "#facc15"
RED      = "#f87171"
BLUE     = "#60a5fa"
ORANGE   = "#fb923c"
PURPLE   = "#c084fc"
GRID     = "#2a2d3a"
TEXT     = "#e2e8f0"
SUBTEXT  = "#94a3b8"

COL_LABELS = {
    "st_met":     "st_met (metallicity)",
    "pl_orbsmax": "pl_orbsmax (semi-major axis)",
    "sy_dist":    "sy_dist (system distance)",
    "pl_orbper":  "pl_orbper (orbital period)",
    "st_teff":    "st_teff (stellar temp)",
    "st_rad":     "st_rad (stellar radius)",
    "st_mass":    "st_mass (stellar mass)",
    "pl_bmasse":  "pl_bmasse (planet mass)",
    "pl_rade":    "pl_rade (planet radius)",
}

BASE_LAYOUT = dict(
    paper_bgcolor=DARK_BG,
    plot_bgcolor=PANEL_BG,
    font=dict(color=TEXT, family="monospace"),
    margin=dict(l=20, r=20, t=50, b=40),
)

# ── Figures ───────────────────────────────────────────────────────────────────
def panel1():
    labels = [COL_LABELS[c] for c in sorted_cols] + ["pl_eqt (equilibrium temp) ★"]

    present_vals  = [present_pct[c] for c in sorted_cols] + [eqt_measured]
    computed_vals = [0] * len(sorted_cols) + [eqt_computed]
    missing_vals  = [missing_pct[c] for c in sorted_cols] + [eqt_missing]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Present / Measured", y=labels, x=present_vals, orientation="h",
        marker=dict(color=GREEN, opacity=0.85),
        hovertemplate="%{y}<br>Present: %{x:.1f}%<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        name="Computed (derived)", y=labels, x=computed_vals, orientation="h",
        marker=dict(color=YELLOW, opacity=0.85),
        hovertemplate="%{y}<br>Computed: %{x:.1f}%<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        name="Missing", y=labels, x=missing_vals, orientation="h",
        marker=dict(color=RED, opacity=0.6),
        hovertemplate="%{y}<br>Missing: %{x:.1f}%<extra></extra>",
    ))
    fig.update_layout(
        **BASE_LAYOUT,
        barmode="stack",
        title=dict(text="Panel 1 — Column Completeness Profile", font=dict(size=14)),
        xaxis=dict(range=[0, 115], tickvals=[0, 25, 50, 75, 100], gridcolor=GRID,
                   title=dict(text="% of 1,173 records", font=dict(color=SUBTEXT))),
        yaxis=dict(gridcolor=GRID),
        legend=dict(orientation="h", yanchor="bottom", y=1.01, x=0,
                    bgcolor="rgba(0,0,0,0)"),
        shapes=[dict(type="line", x0=100, x1=100,
                     y0=-0.5, y1=len(labels) - 0.5,
                     line=dict(color=GRID, dash="dash", width=1))],
        annotations=[dict(
            x=49, y=len(sorted_cols),
            text="★ measured ≠ computed<br>(reliability flag, not error)",
            showarrow=True, ax=-80, ay=30,
            font=dict(color=YELLOW, size=10),
            arrowcolor=YELLOW, arrowwidth=1,
        )],
    )
    return fig


def panel2():
    colors_p2 = {"st_met": RED, "pl_orbsmax": ORANGE, "sy_dist": BLUE}
    line_labels = {
        "st_met":     "st_met (metallicity)",
        "pl_orbsmax": "pl_orbsmax (semi-major axis)",
        "sy_dist":    "sy_dist (distance)",
    }
    fig = go.Figure()
    for col in watch_cols:
        fig.add_trace(go.Scatter(
            x=valid_years, y=completeness_by_year[col],
            name=line_labels[col], mode="lines+markers",
            line=dict(color=colors_p2[col], width=2),
            marker=dict(size=4),
            hovertemplate=f"{line_labels[col]}<br>Year: %{{x:.0f}}<br>Complete: %{{y:.1f}}%<extra></extra>",
        ))
    for yr, lbl in [(2009, "Kepler"), (2018, "TESS")]:
        fig.add_vline(x=yr, line=dict(color=PURPLE, dash="dash", width=1.3), opacity=0.75)
        fig.add_annotation(x=yr + 0.3, y=106, text=lbl, textangle=-90,
                           font=dict(color=PURPLE, size=10), showarrow=False)

    all_vals = [v for vals in completeness_by_year.values() for v in vals]
    fig.add_annotation(
        x=valid_years[0] + 0.5, y=max(0, min(all_vals) - 2),
        text="⚠ small n (<10/yr)", showarrow=False,
        font=dict(color=SUBTEXT, size=10),
    )
    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(text="Panel 2 — Completeness Over Time (worst offenders)", font=dict(size=14)),
        xaxis=dict(title=dict(text="Discovery year", font=dict(color=SUBTEXT)), gridcolor=GRID),
        yaxis=dict(title=dict(text="% complete (non-null)", font=dict(color=SUBTEXT)),
                   gridcolor=GRID, range=[max(0, min(all_vals) - 5), 110]),
        legend=dict(x=0.01, y=0.01, bgcolor="rgba(0,0,0,0)"),
    )
    return fig


def timeline():
    yc = df["disc_year"].value_counts().sort_index()
    bar_colors = [
        PURPLE if y >= 2023 else BLUE if y >= 2018 else GREEN if y >= 2009 else SUBTEXT
        for y in yc.index
    ]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=yc.index, y=yc.values,
        marker_color=bar_colors, marker_opacity=0.85,
        hovertemplate="Year: %{x:.0f}<br>Discoveries: %{y}<extra></extra>",
        showlegend=False,
    ))
    for yr, lbl in [(2009, "Kepler"), (2018, "TESS")]:
        fig.add_vline(x=yr, line=dict(color=YELLOW, dash="dash", width=1.3), opacity=0.8)
        fig.add_annotation(x=yr + 0.3, y=yc.values.max() * 0.9, text=lbl, textangle=-90,
                           font=dict(color=YELLOW, size=10), showarrow=False)
    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(text="Discovery Rate by Year", font=dict(size=14)),
        xaxis=dict(title=dict(text="Discovery year", font=dict(color=SUBTEXT)), gridcolor=GRID),
        yaxis=dict(title=dict(text="Planets discovered", font=dict(color=SUBTEXT)), gridcolor=GRID),
    )
    return fig


# ── Stats ─────────────────────────────────────────────────────────────────────
unique_stars = df["hostname"].nunique() if "hostname" in df.columns else "—"
disc_range   = f"{int(df['disc_year'].min())}–{int(df['disc_year'].max())}"

def stat_card(value, label, color=BLUE):
    return html.Div([
        html.Div(value, style={"color": color, "fontSize": "26px", "fontWeight": "bold"}),
        html.Div(label, style={"color": SUBTEXT, "fontSize": "11px"}),
    ], style={"textAlign": "center"})


# ── Layout ────────────────────────────────────────────────────────────────────
app = dash.Dash(__name__)
app.title = "Exoplanet Data Quality Audit"

app.layout = html.Div(
    style={"backgroundColor": DARK_BG, "minHeight": "100vh",
           "padding": "24px 32px", "fontFamily": "monospace"},
    children=[

        # Header
        html.H1("Exoplanet Catalog — Data Quality Audit",
                style={"color": TEXT, "textAlign": "center",
                       "margin": "0 0 6px 0", "fontSize": "26px"}),
        html.P(
            "Completeness is uneven and systematic: expensive columns are sparse, "
            "some values are derived not measured, and recent discoveries are shallower.",
            style={"color": SUBTEXT, "textAlign": "center", "fontStyle": "italic",
                   "margin": "0 0 24px 0", "fontSize": "13px"},
        ),

        # Stats row
        html.Div(
            style={"display": "flex", "justifyContent": "center",
                   "gap": "40px", "marginBottom": "24px"},
            children=[
                stat_card("1,173",  "exoplanet records"),
                stat_card(str(unique_stars), "star systems"),
                stat_card("96%",    "transit-detected"),
                stat_card(disc_range, "discovery years"),
                stat_card(f"{missing_pct['st_met']:.1f}%", "st_met missing (worst)", RED),
                stat_card(f"{eqt_computed:.1f}%", "pl_eqt computed (derived)", YELLOW),
            ],
        ),

        # Panel 1 + Panel 2
        html.Div(
            style={"display": "grid", "gridTemplateColumns": "1fr 1fr",
                   "gap": "16px", "marginBottom": "16px"},
            children=[
                dcc.Graph(figure=panel1(), config={"displayModeBar": False},
                          style={"height": "420px"}),
                dcc.Graph(figure=panel2(), config={"displayModeBar": False},
                          style={"height": "420px"}),
            ],
        ),

        # Timeline
        dcc.Graph(figure=timeline(), config={"displayModeBar": False},
                  style={"height": "280px"}),
    ],
)

if __name__ == "__main__":
    app.run(debug=True)
