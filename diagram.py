import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import data_prep

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

col_labels = {
    "st_met":     "st_met  (stellar metallicity)",
    "pl_orbsmax": "pl_orbsmax  (semi-major axis)",
    "sy_dist":    "sy_dist  (system distance)",
    "pl_orbper":  "pl_orbper  (orbital period)",
    "st_teff":    "st_teff  (stellar temperature)",
    "st_rad":     "st_rad  (stellar radius)",
    "st_mass":    "st_mass  (stellar mass)",
    "pl_bmasse":  "pl_bmasse  (planet mass)",
    "pl_rade":    "pl_rade  (planet radius)",
}

# Sort all by completeness ascending (worst at top)
sorted_cols = sorted(profile_cols, key=lambda c: present_pct[c])

# ── Figure ────────────────────────────────────────────────────────────────────
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

fig = plt.figure(figsize=(16, 11), facecolor=DARK_BG)
fig.suptitle(
    "Exoplanet Catalog — Data Quality Audit",
    fontsize=17, fontweight="bold", color=TEXT, y=0.97
)
fig.text(
    0.5, 0.935,
    "Completeness is uneven and systematic: expensive columns are sparse, "
    "some values are derived not measured, and recent discoveries are shallower.",
    ha="center", fontsize=10, color=SUBTEXT, style="italic"
)

gs = fig.add_gridspec(1, 2, left=0.03, right=0.97, top=0.90, bottom=0.08,
                      wspace=0.38)
ax1 = fig.add_subplot(gs[0])
ax2 = fig.add_subplot(gs[1])

for ax in [ax1, ax2]:
    ax.set_facecolor(PANEL_BG)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID)

# ── Panel 1: Column Completeness Profile ─────────────────────────────────────
bar_h = 0.6
labels_p1 = []

for i, col in enumerate(sorted_cols):
    pct = present_pct[col]
    mis = missing_pct[col]
    ax1.barh(i, pct, height=bar_h, color=GREEN, alpha=0.85, zorder=3)
    ax1.barh(i, mis, height=bar_h, left=pct, color=RED, alpha=0.6, zorder=3)
    ax1.text(101, i, f"{pct:.1f}%", va="center", fontsize=8.5,
             color=TEXT, fontweight="bold")
    labels_p1.append(col_labels[col])

# pl_eqt special row at top
eqt_i = len(sorted_cols)
ax1.barh(eqt_i, eqt_measured, height=bar_h, color=GREEN, alpha=0.85, zorder=3,
         label="Measured / Present")
ax1.barh(eqt_i, eqt_computed, height=bar_h, left=eqt_measured,
         color=YELLOW, alpha=0.85, zorder=3, label="Computed (derived)")
if eqt_missing > 0:
    ax1.barh(eqt_i, eqt_missing, height=bar_h,
             left=eqt_measured + eqt_computed, color=RED, alpha=0.6, zorder=3)
ax1.text(101, eqt_i,
         f"{eqt_measured:.1f}% meas / {eqt_computed:.1f}% comp",
         va="center", fontsize=8, color=YELLOW)
labels_p1.append("pl_eqt  (equilibrium temp)  ★")

ax1.set_yticks(range(len(labels_p1)))
ax1.set_yticklabels(labels_p1, fontsize=9, color=TEXT)
ax1.set_xlim(0, 130)
ax1.set_xlabel("% of 1,173 records", fontsize=9, color=SUBTEXT)
ax1.set_title("Panel 1 — Column Completeness Profile",
              fontsize=11, color=TEXT, pad=10, fontweight="bold")
ax1.axvline(100, color=GRID, linewidth=1, linestyle="--", zorder=2)
ax1.xaxis.set_tick_params(colors=SUBTEXT)
ax1.set_xticks([0, 25, 50, 75, 100])
ax1.tick_params(axis="x", colors=SUBTEXT, labelsize=8)
ax1.grid(axis="x", color=GRID, linewidth=0.5, zorder=1)

# Annotation for pl_eqt
ax1.annotate("★ measured ≠ computed\n   (reliability flag, not error)",
             xy=(50, eqt_i), xytext=(20, eqt_i - 1.6),
             fontsize=7.5, color=YELLOW,
             arrowprops=dict(arrowstyle="->", color=YELLOW, lw=0.8))

# Legend p1
p1_legend = [
    mpatches.Patch(color=GREEN,  alpha=0.85, label="Present / Measured"),
    mpatches.Patch(color=YELLOW, alpha=0.85, label="Computed (derived)"),
    mpatches.Patch(color=RED,    alpha=0.6,  label="Missing"),
]
ax1.legend(handles=p1_legend, loc="lower right", fontsize=8,
           facecolor=DARK_BG, edgecolor=GRID, labelcolor=TEXT)

# ── Panel 2: Completeness Over Time ──────────────────────────────────────────
colors_p2 = {"st_met": RED, "pl_orbsmax": ORANGE, "sy_dist": BLUE}
line_labels = {
    "st_met":     "st_met  (stellar metallicity)",
    "pl_orbsmax": "pl_orbsmax  (semi-major axis)",
    "sy_dist":    "sy_dist  (system distance)",
}

for col in watch_cols:
    ax2.plot(valid_years, completeness_by_year[col],
             color=colors_p2[col], linewidth=2, marker="o",
             markersize=3, label=line_labels[col], zorder=3)

# Structural break annotations
for launch_year, label, offset in [(2009, "Kepler", 8), (2018, "TESS", 8)]:
    if min(valid_years) <= launch_year <= max(valid_years):
        ax2.axvline(launch_year, color=PURPLE, linewidth=1.2,
                    linestyle="--", alpha=0.7, zorder=2)
        ax2.text(launch_year + 0.3, 72 + offset, label,
                 fontsize=8, color=PURPLE, rotation=90, va="bottom")

ax2.set_xlim(min(valid_years) - 0.5, max(valid_years) + 0.5)
all_vals = [v for vals in completeness_by_year.values() for v in vals]
ax2.set_ylim(max(0, min(all_vals) - 5), 103)
ax2.set_xlabel("Discovery year", fontsize=9, color=SUBTEXT)
ax2.set_ylabel("% complete (non-null)", fontsize=9, color=SUBTEXT)
ax2.set_title("Panel 2 — Completeness Over Time (worst offenders)",
              fontsize=11, color=TEXT, pad=10, fontweight="bold")
ax2.tick_params(colors=SUBTEXT, labelsize=8)
ax2.grid(color=GRID, linewidth=0.5, zorder=1)
ax2.legend(fontsize=8.5, facecolor=DARK_BG, edgecolor=GRID, labelcolor=TEXT)

# Callout: small sample early years
ax2.text(min(valid_years) + 0.2, 62,
         "⚠ small n\n(<10 planets/yr)",
         fontsize=7.5, color=SUBTEXT, va="bottom")

# ── Save ──────────────────────────────────────────────────────────────────────
plt.savefig("design_diagram.png", dpi=150, bbox_inches="tight",
            facecolor=DARK_BG)
print("Saved: design_diagram.png")
