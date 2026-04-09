# PLAN.md — Stars Data Quality Audit

Derived from `DESIGN.md`. Covers implementation phases, scoped deliverables, and verification
criteria for the two-panel data quality visualization.

---

## Overview

| Phase | Deliverable | Status |
|---|---|---|
| 1. Data Preparation | Computed metrics (missingness rates, conditional missingness by metallicity group) | Done |
| 2. Panel 1 | Horizontal bar chart — column completeness profile | Done |
| 3. Panel 2 | Grouped bar chart — conditional missingness when metallicity is absent vs. present | Done |
| 4. Composition | Two-panel figure with shared title and subtitle | Done |
| 5. Presentation | 7-slide deck with narrative context | Done |

---

## Phase 1 — Data Preparation

**Scope:** Load `stars.csv` and compute the two metric sets that feed both panels.

### Deliverables

| Metric | Computation | Output variable |
|---|---|---|
| Per-column % missing | `df[col].isna().sum() / n * 100` | `missing_pct[col]` |
| Per-column % present | `100 - missing_pct[col]` | `present_pct[col]` |
| Group mask: met absent | `df["metallicity_fe_h"].isna()` | `met_missing_mask` |
| Conditional missing (met absent) | `df[met_missing_mask][col].isna().mean() * 100` | `cond_missing_absent[col]` |
| Conditional missing (met present) | `df[~met_missing_mask][col].isna().mean() * 100` | `cond_missing_present[col]` |
| Group sizes | `met_missing_mask.sum()`, `(~met_missing_mask).sum()` | `n_absent`, `n_present` |

### Verification Criteria

- `missing_pct["metallicity_fe_h"]` ≈ 6.2% and is the largest value across all profiled columns
- `present_pct[col] + missing_pct[col] == 100.0` for all columns (within float tolerance)
- `n_absent + n_present == 972` (total row count)
- `cond_missing_absent["teff_k"]` ≈ 25% and `cond_missing_present["teff_k"]` ≈ 0.1%
- All conditional missingness values are in `[0, 100]` — no negative or >100 values

---

## Phase 2 — Panel 1: Column Completeness Profile

**Scope:** Horizontal bar chart covering claim A (missingness is concentrated in metallicity).
One bar per analytically important column, sorted worst-to-best.

### Deliverables

| Element | Specification |
|---|---|
| Chart type | `barh` — horizontal bars |
| Columns profiled | `metallicity_fe_h`, `teff_k`, `distance_pc`, `radius_solar`, `mass_solar` |
| Sort order | Ascending completeness — worst offender (`metallicity_fe_h`) at bottom |
| Bar segments | Green = present · Red = missing |
| % labels | Right-aligned, showing completeness percentage per row |
| Legend | Two-item patch legend: Present · Missing |
| Reference line | Dashed vertical at x=100 |

### Verification Criteria

- `metallicity_fe_h` bar is visually the shortest (worst completeness); `mass_solar` is longest
- No bar exceeds x=100 (present + missing segments must sum to exactly 100)
- All five columns are present and labeled
- Legend is visible and does not obscure data

---

## Phase 3 — Panel 2: Conditional Missingness

**Scope:** Grouped bar chart covering claims B (missing metallicity predicts missing
everything else) and C (distance does not explain it). One pair of bars per secondary column,
grouped by whether `metallicity_fe_h` is absent or present.

### Deliverables

| Element | Specification |
|---|---|
| Chart type | Grouped `bar` — two bars per column |
| Columns shown | `teff_k` · `mass_solar` · `radius_solar` · `distance_pc` |
| Groups | Metallicity absent (n=60, darker color) · Metallicity present (n=912, lighter color) |
| Y-axis | % missing (0–30%); data-driven ceiling — `max(all_values) * 1.15` |
| Value labels | On top of each bar showing exact % |
| Group size annotation | Subtitle or footer: "metallicity absent: n=60 · metallicity present: n=912" |
| Distance callout | Text annotation noting median distance is similar for both groups (~255 pc vs. ~290 pc) |
| Legend | Two-item: Metallicity absent · Metallicity present |

### Verification Criteria

- For every column, the "metallicity absent" bar is taller than the "metallicity present" bar
- `teff_k` absent bar is approximately 25% — largest visible difference
- `mass_solar` absent bar is approximately 6.7%
- Y-axis ceiling is above the tallest bar — no data is clipped
- Distance callout is present and readable without overlapping bars
- Group size annotation (n=60, n=912) is visible

---

## Phase 4 — Composition

**Scope:** Combine Panel 1 and Panel 2 into a single figure with shared framing.
Implemented in `diagram.py`.

### Deliverables

| Element | Specification |
|---|---|
| Layout | 1×2 grid (`gridspec`), Panels 1 and 2 side by side |
| Figure title | "Stars Catalog — Data Quality Audit" |
| Subtitle | One-sentence story hypothesis (italic, subdued color) |
| Color scheme | Dark background (`#0f1117`) — consistent with presentation deck |
| Output | `design_diagram.png` at 150 dpi |

### Verification Criteria

- Figure renders without matplotlib warnings
- Title and subtitle are fully visible (not clipped by figure boundary)
- Both panels share the same background color and font palette
- PNG file size < 500 KB (sanity check for resolution/content)
- Running `python3 diagram.py` from the repo root produces `design_diagram.png`

---

## Phase 5 — Presentation

**Scope:** 7-slide PowerPoint deck translating the visualization into a narrative for
a practitioner audience. Implemented in `build_ppt.py`.

### Slide Map

| Slide | Title | Covers |
|---|---|---|
| 1 | Title | Audience framing |
| 2 | The Dataset | Context: 972 records, column overview |
| 3 | Story Hypothesis | Claims A, B, C |
| 4 | Column Completeness Profile | Panel 1 chart + callout text |
| 5 | Conditional Missingness | Panel 2 chart + callout text |
| 6 | Risks & Caveats | 5 documented risks from DESIGN.md |
| 7 | What We Built | Methodology summary |

### Verification Criteria

- Running `python3 build_ppt.py` from the repo root produces `stars_data_quality_audit.pptx`
- All 7 slides render without errors in PowerPoint / LibreOffice / macOS Preview
- Slide 4 chart matches Panel 1 produced by `diagram.py` (same data, same sort order)
- Slide 5 chart matches Panel 2 (same bars, same annotations)
- Slide 7 reads as a completed retrospective, not a forward plan

---

## Reproduction

```bash
pip install -r requirements.txt
python3 diagram.py        # → design_diagram.png
python3 build_ppt.py      # → stars_data_quality_audit.pptx
```

Both scripts are idempotent — re-running overwrites existing outputs with identical results
given the same input data.

---

## Known Constraints

| Constraint | Detail |
|---|---|
| Small absent group | Only 60 stars (6.2%) lack metallicity; conditional rates have wider uncertainty bands — flag on Panel 2 |
| Co-missingness vs. causality | Missing metallicity correlates with, but does not cause, missing other columns — frame as "data-sparse stars", not "metallicity gap causes other gaps" |
| Snapshot data | `stars.csv` is a point-in-time pull; stars currently missing data may gain measurements over time |
| No time dimension | Dataset contains no discovery year; temporal completeness trends cannot be computed from this file |
| `metallicity_fe_h` outlier status | 6.2% vs. <2% for peers — flag as "investigate before using as feature" rather than "don't use" |
