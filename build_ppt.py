import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
import io

# ── Palette ───────────────────────────────────────────────────────────────────
DARK_BG   = "#0f1117"
PANEL_BG  = "#1a1d27"
GREEN     = "#4ade80"
YELLOW    = "#facc15"
RED       = "#f87171"
BLUE      = "#60a5fa"
ORANGE    = "#fb923c"
PURPLE    = "#c084fc"
GRID      = "#2a2d3a"
TEXT      = "#e2e8f0"
SUBTEXT   = "#94a3b8"

def hex_rgb(h):
    h = h.lstrip("#")
    return RGBColor(int(h[0:2],16), int(h[2:4],16), int(h[4:6],16))

def mpl_to_stream(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    buf.seek(0)
    return buf

# ── Load data ─────────────────────────────────────────────────────────────────
df = pd.read_csv("exoplanets.csv")
n  = len(df)

# ── Chart helpers ─────────────────────────────────────────────────────────────
profile_cols = ["st_met","pl_orbsmax","sy_dist","pl_orbper",
                "st_teff","st_rad","st_mass","pl_bmasse","pl_rade"]
col_labels = {
    "st_met":     "st_met  (metallicity)",
    "pl_orbsmax": "pl_orbsmax  (semi-major axis)",
    "sy_dist":    "sy_dist  (system distance)",
    "pl_orbper":  "pl_orbper  (orbital period)",
    "st_teff":    "st_teff  (stellar temp)",
    "st_rad":     "st_rad  (stellar radius)",
    "st_mass":    "st_mass  (stellar mass)",
    "pl_bmasse":  "pl_bmasse  (planet mass)",
    "pl_rade":    "pl_rade  (planet radius)",
}
missing_pct = {c: df[c].isna().sum()/n*100 for c in profile_cols}
present_pct = {c: 100-missing_pct[c] for c in profile_cols}
sorted_cols = sorted(profile_cols, key=lambda c: present_pct[c])

eqt_missing  = df["pl_eqt"].isna().sum()/n*100
eqt_computed = df["pl_eqt_computed"].sum()/n*100
eqt_measured = 100 - eqt_missing - eqt_computed

watch_cols = ["st_met","pl_orbsmax","sy_dist"]
year_counts = df["disc_year"].value_counts()
valid_years = sorted([y for y in df["disc_year"].dropna().unique()
                      if year_counts[y] >= 5])
completeness_by_year = {
    c: [(1 - df[df["disc_year"]==y][c].isna().mean())*100 for y in valid_years]
    for c in watch_cols
}

# ── Chart 1: Column profile ────────────────────────────────────────────────────
def make_panel1():
    fig, ax = plt.subplots(figsize=(10, 6), facecolor=DARK_BG)
    ax.set_facecolor(PANEL_BG)
    bar_h = 0.6
    all_cols = sorted_cols + ["pl_eqt"]
    labels = [col_labels[c] for c in sorted_cols] + ["pl_eqt  (equilibrium temp)  ★"]
    for i, col in enumerate(sorted_cols):
        ax.barh(i, present_pct[col], height=bar_h, color=GREEN, alpha=0.85, zorder=3)
        ax.barh(i, missing_pct[col], height=bar_h, left=present_pct[col],
                color=RED, alpha=0.6, zorder=3)
        ax.text(101, i, f"{present_pct[col]:.1f}%", va="center",
                fontsize=9, color=TEXT, fontweight="bold")
    eqt_i = len(sorted_cols)
    ax.barh(eqt_i, eqt_measured, height=bar_h, color=GREEN, alpha=0.85, zorder=3)
    ax.barh(eqt_i, eqt_computed, height=bar_h, left=eqt_measured,
            color=YELLOW, alpha=0.85, zorder=3)
    ax.text(101, eqt_i, f"{eqt_measured:.1f}% / {eqt_computed:.1f}% comp",
            va="center", fontsize=8, color=YELLOW)
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=9.5, color=TEXT)
    ax.set_xlim(0, 135)
    ax.set_xlabel("% of 1,173 records", fontsize=9, color=SUBTEXT)
    ax.set_title("Column Completeness Profile", fontsize=13,
                 color=TEXT, fontweight="bold", pad=12)
    ax.axvline(100, color=GRID, linewidth=1, linestyle="--", zorder=2)
    ax.set_xticks([0,25,50,75,100])
    ax.tick_params(colors=SUBTEXT, labelsize=8)
    ax.grid(axis="x", color=GRID, linewidth=0.5, zorder=1)
    for spine in ax.spines.values(): spine.set_edgecolor(GRID)
    legend = [
        mpatches.Patch(color=GREEN,  alpha=0.85, label="Present / Measured"),
        mpatches.Patch(color=YELLOW, alpha=0.85, label="Computed (derived)"),
        mpatches.Patch(color=RED,    alpha=0.6,  label="Missing"),
    ]
    ax.legend(handles=legend, fontsize=8.5, facecolor=DARK_BG,
              edgecolor=GRID, labelcolor=TEXT, loc="lower right")
    fig.tight_layout()
    return fig

# ── Chart 2: Completeness over time ──────────────────────────────────────────
def make_panel2():
    colors_p2 = {"st_met": RED, "pl_orbsmax": ORANGE, "sy_dist": BLUE}
    line_labels = {
        "st_met":     "st_met  (metallicity)",
        "pl_orbsmax": "pl_orbsmax  (semi-major axis)",
        "sy_dist":    "sy_dist  (distance)",
    }
    fig, ax = plt.subplots(figsize=(10, 6), facecolor=DARK_BG)
    ax.set_facecolor(PANEL_BG)
    for col in watch_cols:
        ax.plot(valid_years, completeness_by_year[col],
                color=colors_p2[col], linewidth=2.2, marker="o",
                markersize=3.5, label=line_labels[col], zorder=3)
    for yr, lbl, yo in [(2009,"Kepler",8),(2018,"TESS",14)]:
        ax.axvline(yr, color=PURPLE, linewidth=1.3, linestyle="--", alpha=0.75, zorder=2)
        ax.text(yr+0.3, 63+yo, lbl, fontsize=9, color=PURPLE, rotation=90, va="bottom")
    ax.set_xlim(min(valid_years)-0.5, max(valid_years)+0.5)
    all_vals = [v for vals in completeness_by_year.values() for v in vals]
    ax.set_ylim(max(0, min(all_vals) - 5), 103)
    ax.set_xlabel("Discovery year", fontsize=9, color=SUBTEXT)
    ax.set_ylabel("% complete (non-null)", fontsize=9, color=SUBTEXT)
    ax.set_title("Completeness Over Time — Worst Offenders", fontsize=13,
                 color=TEXT, fontweight="bold", pad=12)
    ax.tick_params(colors=SUBTEXT, labelsize=8)
    ax.grid(color=GRID, linewidth=0.5, zorder=1)
    for spine in ax.spines.values(): spine.set_edgecolor(GRID)
    ax.legend(fontsize=9, facecolor=DARK_BG, edgecolor=GRID, labelcolor=TEXT)
    ax.text(min(valid_years)+0.2, 62, "⚠ small n (<10/yr)",
            fontsize=7.5, color=SUBTEXT, va="bottom")
    fig.tight_layout()
    return fig

# ── Chart 3: Discovery timeline bar ──────────────────────────────────────────
def make_timeline():
    year_counts_all = df["disc_year"].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(10, 4), facecolor=DARK_BG)
    ax.set_facecolor(PANEL_BG)
    colors = [PURPLE if y >= 2023 else BLUE if y >= 2018 else GREEN if y >= 2009 else SUBTEXT
              for y in year_counts_all.index]
    ax.bar(year_counts_all.index, year_counts_all.values, color=colors, alpha=0.85, zorder=3)
    for yr, lbl in [(2009,"Kepler"),(2018,"TESS")]:
        ax.axvline(yr, color=YELLOW, linewidth=1.3, linestyle="--", alpha=0.8, zorder=2)
        ax.text(yr+0.3, year_counts_all.values.max()*0.85,
                lbl, fontsize=9, color=YELLOW, rotation=90, va="top")
    ax.set_xlabel("Discovery year", fontsize=9, color=SUBTEXT)
    ax.set_ylabel("Planets discovered", fontsize=9, color=SUBTEXT)
    ax.set_title("Discovery Rate by Year", fontsize=13,
                 color=TEXT, fontweight="bold", pad=12)
    ax.tick_params(colors=SUBTEXT, labelsize=8)
    ax.grid(axis="y", color=GRID, linewidth=0.5, zorder=1)
    for spine in ax.spines.values(): spine.set_edgecolor(GRID)
    legend = [
        mpatches.Patch(color=SUBTEXT, label="Pre-Kepler (–2008)"),
        mpatches.Patch(color=GREEN,   label="Kepler era (2009–2017)"),
        mpatches.Patch(color=BLUE,    label="TESS era (2018–2022)"),
        mpatches.Patch(color=PURPLE,  label="Recent surge (2023–)"),
    ]
    ax.legend(handles=legend, fontsize=8, facecolor=DARK_BG,
              edgecolor=GRID, labelcolor=TEXT)
    fig.tight_layout()
    return fig

# ── Build presentation ────────────────────────────────────────────────────────
prs = Presentation()
prs.slide_width  = Inches(13.33)
prs.slide_height = Inches(7.5)

BLANK = 6  # blank layout index

def blank_slide():
    return prs.slides.add_slide(prs.slide_layouts[BLANK])

def bg(slide):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = hex_rgb(DARK_BG)

def add_text(slide, text, left, top, width, height,
             size=24, bold=False, color=TEXT, align=PP_ALIGN.LEFT, wrap=True):
    txb = slide.shapes.add_textbox(Inches(left), Inches(top),
                                   Inches(width), Inches(height))
    txb.word_wrap = wrap
    tf = txb.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = hex_rgb(color)
    return txb

def add_img(slide, stream, left, top, width):
    slide.shapes.add_picture(stream, Inches(left), Inches(top), width=Inches(width))

def divider(slide, top=1.15):
    line = slide.shapes.add_connector(1,
        Inches(0.5), Inches(top), Inches(12.83), Inches(top))
    line.line.color.rgb = hex_rgb(GRID)
    line.line.width = Pt(1)

# ── Slide 1: Title ────────────────────────────────────────────────────────────
sl = blank_slide(); bg(sl)
add_text(sl, "Exoplanet Catalog", 1.0, 1.8, 11.0, 1.2,
         size=44, bold=True, color=TEXT, align=PP_ALIGN.CENTER)
add_text(sl, "Data Quality Audit", 1.0, 2.9, 11.0, 0.8,
         size=32, bold=False, color=BLUE, align=PP_ALIGN.CENTER)
add_text(sl,
    "Understanding completeness, derived values, and recency gaps\n"
    "before modeling or analysis",
    1.5, 3.9, 10.0, 1.0, size=16, color=SUBTEXT, align=PP_ALIGN.CENTER)
add_text(sl, "Audience: Data Practitioner", 1.0, 6.6, 11.0, 0.5,
         size=12, color=SUBTEXT, align=PP_ALIGN.CENTER)

# ── Slide 2: Dataset snapshot ─────────────────────────────────────────────────
sl = blank_slide(); bg(sl)
add_text(sl, "The Dataset", 0.5, 0.35, 12.0, 0.7,
         size=28, bold=True, color=TEXT)
divider(sl)

stats = [
    ("1,173", "exoplanet records"),
    ("972",   "unique star systems"),
    ("19",    "columns"),
    ("96%",   "transit-detected"),
    ("2002–2025", "discovery years"),
]
for i,(val,lbl) in enumerate(stats):
    x = 0.5 + i*2.55
    add_text(sl, val, x, 1.4, 2.4, 0.75, size=30, bold=True, color=BLUE, align=PP_ALIGN.CENTER)
    add_text(sl, lbl, x, 2.1, 2.4, 0.45, size=12, color=SUBTEXT, align=PP_ALIGN.CENTER)

fig = make_timeline()
add_img(sl, mpl_to_stream(fig), 0.5, 2.75, 12.3)
plt.close(fig)

add_text(sl,
    "Discovery rate exploded after Kepler (2009) and again after TESS (2018). "
    "More planets ≠ more complete data.",
    0.5, 6.8, 12.3, 0.5, size=11, color=SUBTEXT)

# ── Slide 3: Story hypothesis ─────────────────────────────────────────────────
sl = blank_slide(); bg(sl)
add_text(sl, "Story Hypothesis", 0.5, 0.35, 12.0, 0.7,
         size=28, bold=True, color=TEXT)
divider(sl)
add_text(sl,
    "Completeness in this catalog is uneven and systematic.",
    0.5, 1.35, 12.0, 0.6, size=20, bold=True, color=BLUE)

claims = [
    (GREEN,  "A",
     "Missingness is structured, not random",
     "st_met (metallicity) is missing 7× more than peer columns. "
     "Spectrometry costs more than photometry — the gaps reflect measurement economics."),
    (YELLOW, "B",
     "Measured ≠ computed",
     "pl_eqt_computed flags temperatures derived from stellar models vs. directly observed. "
     "A reliability dimension invisible without reading the schema."),
    (ORANGE, "C",
     "Recent discoveries are shallower",
     "100+ planets/year since 2023. High-volume survey planets have less follow-up data "
     "than earlier discoveries. More rows, thinner rows."),
]
for i,(color,letter,title,body) in enumerate(claims):
    y = 2.1 + i*1.5
    add_text(sl, letter, 0.5, y, 0.5, 0.55, size=26, bold=True, color=color)
    add_text(sl, title, 1.1, y, 11.2, 0.45, size=16, bold=True, color=color)
    add_text(sl, body,  1.1, y+0.45, 11.2, 0.9, size=12, color=SUBTEXT)

# ── Slide 4: Panel 1 ─────────────────────────────────────────────────────────
sl = blank_slide(); bg(sl)
add_text(sl, "Column Completeness Profile", 0.5, 0.35, 12.0, 0.7,
         size=28, bold=True, color=TEXT)
divider(sl)
add_text(sl, "Covers claims A + B", 0.5, 1.2, 4.0, 0.4,
         size=13, color=SUBTEXT)

fig = make_panel1()
add_img(sl, mpl_to_stream(fig), 0.4, 1.55, 12.5)
plt.close(fig)

add_text(sl,
    "st_met stands alone at 92.6% — 7× worse than peers.  "
    "pl_eqt bar is split: green = directly observed, yellow = derived from stellar model.",
    0.5, 6.85, 12.3, 0.5, size=10.5, color=SUBTEXT)

# ── Slide 5: Panel 2 ─────────────────────────────────────────────────────────
sl = blank_slide(); bg(sl)
add_text(sl, "Completeness Over Time — Worst Offenders", 0.5, 0.35, 12.0, 0.7,
         size=28, bold=True, color=TEXT)
divider(sl)
add_text(sl, "Covers claim C", 0.5, 1.2, 4.0, 0.4, size=13, color=SUBTEXT)

fig = make_panel2()
add_img(sl, mpl_to_stream(fig), 0.4, 1.55, 12.5)
plt.close(fig)

add_text(sl,
    "st_met completeness dips after TESS ramp-up (2020+). "
    "All columns show volatility pre-2009 due to small sample sizes (<10 planets/yr).",
    0.5, 6.85, 12.3, 0.5, size=10.5, color=SUBTEXT)

# ── Slide 6: Risks ────────────────────────────────────────────────────────────
sl = blank_slide(); bg(sl)
add_text(sl, "Risks & Caveats", 0.5, 0.35, 12.0, 0.7,
         size=28, bold=True, color=TEXT)
divider(sl)

risks = [
    (RED,    "Small year bins",
     "Pre-2009 has <10 planets/year — percentages are noisy. Annotate or bin early years."),
    (YELLOW, "Computed ≠ wrong",
     "pl_eqt_computed is a reliability flag, not an error flag. Derived temperatures can be accurate."),
    (ORANGE, "Snapshot in time",
     "Recent planets gain follow-up data over time. Completeness will improve — this is a point-in-time view."),
    (BLUE,   "Transit bias as confound",
     "96% transit-detected. Missingness may correlate with discovery method, not just recency."),
    (PURPLE, "st_met outlier",
     "7% vs <1% for peers is striking — could be a pipeline artifact. Flag for investigation before use as a feature."),
]
for i,(color,title,body) in enumerate(risks):
    y = 1.25 + i*1.08
    add_text(sl, "▸", 0.5, y, 0.4, 0.4, size=14, bold=True, color=color)
    add_text(sl, title, 0.95, y, 3.5, 0.38, size=13, bold=True, color=color)
    add_text(sl, body,  0.95, y+0.38, 11.5, 0.6, size=11, color=SUBTEXT)

# ── Slide 7: What we built ────────────────────────────────────────────────────
sl = blank_slide(); bg(sl)
add_text(sl, "What We Built", 0.5, 0.35, 12.0, 0.7,
         size=28, bold=True, color=TEXT)
divider(sl)

steps = [
    (GREEN,  "1", "Computed per-column missingness rates and pl_eqt_computed split from 1,173 records"),
    (GREEN,  "2", "Computed per-year completeness for st_met, pl_orbsmax, and sy_dist"),
    (BLUE,   "3", "Panel 1 — horizontal segmented bar chart (present / computed / missing)"),
    (BLUE,   "4", "Panel 2 — line chart with Kepler (2009) and TESS (2018) structural break annotations"),
    (PURPLE, "5", "7-slide deck documenting the full data quality story for a practitioner audience"),
]
for i,(color,num,text) in enumerate(steps):
    y = 1.35 + i*0.95
    add_text(sl, num, 0.5, y, 0.5, 0.6, size=22, bold=True, color=color)
    add_text(sl, text, 1.1, y+0.08, 11.0, 0.6, size=15, color=TEXT)

add_text(sl,
    "All outputs are reproducible: run diagram.py for the PNG, build_ppt.py for this deck.",
    0.5, 6.5, 12.3, 0.6, size=12, color=SUBTEXT)

# ── Save ──────────────────────────────────────────────────────────────────────
prs.save("exoplanet_data_quality_audit.pptx")
print("Saved: exoplanet_data_quality_audit.pptx")
