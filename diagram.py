import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
import numpy as np

# ── colours ──────────────────────────────────────────────────────────────────
BG       = "#0f1117"
FG       = "#e8eaf0"
GREEN    = "#4CAF50"
RED      = "#f44336"
ABSENT   = "#FF6B6B"
PRESENT  = "#4ECDC4"
SUBTEXT  = "#9096a8"
GRID     = "#2a2d3a"

# ── load & compute ────────────────────────────────────────────────────────────
df = pd.read_csv("stars.csv")
n  = len(df)

PROFILE_COLS = ["metallicity_fe_h", "teff_k", "distance_pc", "radius_solar", "mass_solar"]
COL_LABELS   = {
    "metallicity_fe_h": "metallicity_fe_h",
    "teff_k":           "teff_k",
    "distance_pc":      "distance_pc",
    "radius_solar":     "radius_solar",
    "mass_solar":       "mass_solar",
}
COND_COLS = ["teff_k", "mass_solar", "radius_solar", "distance_pc"]

missing_pct = {c: df[c].isna().sum() / n * 100 for c in PROFILE_COLS}
present_pct = {c: 100 - missing_pct[c]          for c in PROFILE_COLS}

met_absent  = df["metallicity_fe_h"].isna()
n_absent    = int(met_absent.sum())
n_present   = int((~met_absent).sum())

cond_absent  = {c: df.loc[met_absent,  c].isna().mean() * 100 for c in COND_COLS}
cond_present = {c: df.loc[~met_absent, c].isna().mean() * 100 for c in COND_COLS}

# ── figure setup ─────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(16, 7), facecolor=BG)
gs  = gridspec.GridSpec(1, 2, figure=fig, wspace=0.38,
                        left=0.04, right=0.97, top=0.82, bottom=0.14)
ax1 = fig.add_subplot(gs[0])
ax2 = fig.add_subplot(gs[1])
for ax in (ax1, ax2):
    ax.set_facecolor(BG)
    ax.tick_params(colors=FG, labelsize=9)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID)

# ── figure title & subtitle ───────────────────────────────────────────────────
fig.text(0.5, 0.96, "Stars Catalog — Data Quality Audit",
         ha="center", va="top", fontsize=16, fontweight="bold", color=FG)
fig.text(0.5, 0.90,
         "Missingness is concentrated in metallicity_fe_h (6.2 %), and stars missing "
         "metallicity show dramatically elevated missingness across all other columns.",
         ha="center", va="top", fontsize=9.5, color=SUBTEXT, style="italic")

# ═══════════════════════════════════════════════════════════════════════════════
# PANEL 1 — Column Completeness Profile
# ═══════════════════════════════════════════════════════════════════════════════
# sort ascending by completeness → worst offender at bottom
sorted_cols = sorted(PROFILE_COLS, key=lambda c: present_pct[c])
labels      = [COL_LABELS[c] for c in sorted_cols]
pres_vals   = [present_pct[c] for c in sorted_cols]
miss_vals   = [missing_pct[c] for c in sorted_cols]
y_pos       = np.arange(len(sorted_cols))
bar_h       = 0.55

ax1.barh(y_pos, pres_vals, height=bar_h, color=GREEN, label="Present", zorder=3)
ax1.barh(y_pos, miss_vals, height=bar_h, left=pres_vals, color=RED,   label="Missing", zorder=3)
ax1.axvline(100, color=GRID, linestyle="--", linewidth=0.8, zorder=2)

for i, (p, m) in enumerate(zip(pres_vals, miss_vals)):
    ax1.text(p - 0.5, i, f"{p:.1f}%", ha="right", va="center",
             fontsize=8.5, color=BG, fontweight="bold")

ax1.set_yticks(y_pos)
ax1.set_yticklabels(labels, fontsize=9, color=FG)
ax1.set_xlim(85, 101)
ax1.set_xlabel("% complete", color=FG, fontsize=9)
ax1.set_title("Panel 1 — Column Completeness Profile",
              color=FG, fontsize=10.5, fontweight="bold", pad=10)
ax1.xaxis.grid(True, color=GRID, linewidth=0.5, zorder=0)
ax1.set_axisbelow(True)

p1_legend = [
    mpatches.Patch(color=GREEN, label="Present"),
    mpatches.Patch(color=RED,   label="Missing"),
]
ax1.legend(handles=p1_legend, loc="lower right", fontsize=8,
           framealpha=0.15, labelcolor=FG, facecolor=BG, edgecolor=GRID)

# ═══════════════════════════════════════════════════════════════════════════════
# PANEL 2 — Conditional Missingness
# ═══════════════════════════════════════════════════════════════════════════════
x        = np.arange(len(COND_COLS))
bw       = 0.35
absent_v  = [cond_absent[c]  for c in COND_COLS]
present_v = [cond_present[c] for c in COND_COLS]

bars_abs = ax2.bar(x - bw/2, absent_v,  width=bw, color=ABSENT,  label=f"Met. absent  (n={n_absent})",  zorder=3)
bars_pre = ax2.bar(x + bw/2, present_v, width=bw, color=PRESENT, label=f"Met. present (n={n_present})", zorder=3)

for bar, val in zip(bars_abs, absent_v):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.4,
             f"{val:.1f}%", ha="center", va="bottom", fontsize=8, color=ABSENT, fontweight="bold")
for bar, val in zip(bars_pre, present_v):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.4,
             f"{val:.1f}%", ha="center", va="bottom", fontsize=8, color=PRESENT, fontweight="bold")

col_display = {"teff_k": "teff_k", "mass_solar": "mass_solar",
               "radius_solar": "radius_solar", "distance_pc": "distance_pc"}
ax2.set_xticks(x)
ax2.set_xticklabels([col_display[c] for c in COND_COLS], fontsize=9, color=FG)

y_ceil = max(absent_v) * 1.25
ax2.set_ylim(0, y_ceil)
ax2.set_ylabel("% missing", color=FG, fontsize=9)
ax2.set_title("Panel 2 — Conditional Missingness\n(when metallicity_fe_h is absent vs. present)",
              color=FG, fontsize=10.5, fontweight="bold", pad=10)
ax2.yaxis.grid(True, color=GRID, linewidth=0.5, zorder=0)
ax2.set_axisbelow(True)

# distance callout
dist_i = COND_COLS.index("distance_pc")
ax2.annotate(
    "Median dist. similar:\n~255 pc (present) vs ~290 pc (absent)\n→ distance not the driver",
    xy=(dist_i + bw/2, cond_present["distance_pc"]),
    xytext=(dist_i - 0.15, y_ceil * 0.62),
    fontsize=7.5, color=SUBTEXT, ha="center",
    arrowprops=dict(arrowstyle="->", color=SUBTEXT, lw=0.8),
    bbox=dict(boxstyle="round,pad=0.3", facecolor=BG, edgecolor=GRID, alpha=0.9),
)

ax2.legend(fontsize=8, framealpha=0.15, labelcolor=FG,
           facecolor=BG, edgecolor=GRID, loc="upper right")

# ── save ──────────────────────────────────────────────────────────────────────
plt.savefig("design_diagram.png", dpi=150, facecolor=BG, bbox_inches="tight")
print("Saved design_diagram.png")
