# PLAN.md — Exoplanet Data Quality Audit

Derived from `DESIGN.md`. Covers implementation phases, scoped deliverables, and verification
criteria for the two-panel data quality visualization.

---

## Overview

| Phase | Deliverable | Status |
|---|---|---|
| 1. Data Preparation | Computed metrics (missingness, computed split, year completeness) | Done |
| 2. Panel 1 | Horizontal segmented bar chart — column completeness profile | Done |
| 3. Panel 2 | Line chart — completeness over time for worst offenders | Done |
| 4. Composition | Two-panel figure with shared title and subtitle | Done |
| 5. Presentation | 7-slide deck with narrative context | Done |

---

## Phase 1 — Data Preparation

**Scope:** Load `exoplanets.csv` and compute the three metric sets that feed both panels.

### Deliverables

| Metric | Computation | Output variable |
|---|---|---|
| Per-column % missing | `df[col].isna().sum() / n * 100` | `missing_pct[col]` |
| Per-column % present | `100 - missing_pct[col]` | `present_pct[col]` |
| pl_eqt: % measured | `100 - eqt_missing - eqt_computed` | `eqt_measured` |
| pl_eqt: % computed | `df["pl_eqt_computed"].sum() / n * 100` | `eqt_computed` |
| pl_eqt: % missing | `df["pl_eqt"].isna().sum() / n * 100` | `eqt_missing` |
| Per-year completeness | `(1 - df[year_mask][col].isna().mean()) * 100` | `completeness_by_year[col]` |
| Valid year list | Years with ≥ 5 planets (noise filter) | `valid_years` |

### Verification Criteria

- `missing_pct["st_met"]` ≈ 7% and is the largest value across all profiled columns
- `eqt_measured + eqt_computed + eqt_missing == 100.0` (within float tolerance)
- `valid_years` starts no earlier than 2007 (pre-2007 has <5 planets/year)
- All completeness values are in `[0, 100]` — no negative or >100 values

---

## Phase 2 — Panel 1: Column Completeness Profile

**Scope:** Horizontal bar chart covering claims A (missingness is structured) and B
(measured ≠ computed). One bar per analytically important column, sorted worst-to-best.

### Deliverables

| Element | Specification |
|---|---|
| Chart type | `barh` — horizontal bars |
| Columns profiled | `st_met`, `pl_orbsmax`, `sy_dist`, `pl_orbper`, `st_teff`, `st_rad`, `st_mass`, `pl_bmasse`, `pl_rade` + `pl_eqt` |
| Sort order | Ascending completeness — worst offender (`st_met`) at bottom |
| Bar segments | Green = present/measured · Yellow = computed (pl_eqt only) · Red = missing |
| pl_eqt treatment | Three-way split bar: measured + computed + missing (if any) |
| % labels | Right-aligned, showing completeness percentage per row |
| Annotation | Arrow callout: "measured ≠ computed (reliability flag, not error)" pointing to pl_eqt |
| Legend | Three-item patch legend: Present/Measured · Computed · Missing |
| Reference line | Dashed vertical at x=100 |

### Verification Criteria

- `st_met` bar is visually the shortest (worst completeness); `pl_rade` / `pl_bmasse` are longest
- `pl_eqt` row has a visible yellow segment — confirms computed fraction is non-zero
- No bar exceeds x=100 (present + missing segments must sum to exactly 100)
- Arrow annotation is present and readable without overlapping any bar
- Legend is visible and does not obscure data

---

## Phase 3 — Panel 2: Completeness Over Time

**Scope:** Line chart covering claim C (recent discoveries are shallower). One line per
worst-offender column, x-axis = discovery year, annotated with Kepler and TESS launches.

### Deliverables

| Element | Specification |
|---|---|
| Chart type | Line plot with circle markers |
| Columns plotted | `st_met` (red) · `pl_orbsmax` (orange) · `sy_dist` (blue) |
| X-axis | `disc_year` — valid years only (≥ 5 planets/year) |
| Y-axis | % complete (non-null); floor = `max(0, min_value - 5)` — data-driven, not hardcoded |
| Structural breaks | Dashed vertical lines at 2009 (Kepler) and 2018 (TESS), labelled |
| Small-n callout | Text annotation near early years: "⚠ small n (<10 planets/yr)" |
| Legend | One entry per column with descriptive label |

### Verification Criteria

- `st_met` line is consistently the lowest — it must never cross above `sy_dist` for a majority of years
- Kepler (2009) and TESS (2018) vertical lines fall within the plotted x-axis range
- Y-axis floor is below the minimum observed completeness value — no data is clipped
- Small-n callout appears in the early-year region (left side of x-axis), not overlapping lines
- All three lines are visually distinct (different colors and distinguishable at small sizes)

---

## Phase 4 — Composition

**Scope:** Combine Panel 1 and Panel 2 into a single figure with shared framing.
Implemented in `diagram.py`.

### Deliverables

| Element | Specification |
|---|---|
| Layout | 1×2 grid (`gridspec`), Panels 1 and 2 side by side |
| Figure title | "Exoplanet Catalog — Data Quality Audit" |
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
| 2 | The Dataset | Context: 1,173 records, discovery timeline chart |
| 3 | Story Hypothesis | Claims A, B, C |
| 4 | Column Completeness Profile | Panel 1 chart + callout text |
| 5 | Completeness Over Time | Panel 2 chart + callout text |
| 6 | Risks & Caveats | 5 documented risks from DESIGN.md |
| 7 | What We Built | Methodology summary |

### Verification Criteria

- Running `python3 build_ppt.py` from the repo root produces `exoplanet_data_quality_audit.pptx`
- All 7 slides render without errors in PowerPoint / LibreOffice / macOS Preview
- Slide 4 chart matches the Panel 1 produced by `diagram.py` (same data, same sort order)
- Slide 5 chart matches Panel 2 (same lines, same annotations)
- Slide 7 reads as a completed retrospective, not a forward plan

---

## Reproduction

```bash
pip install -r requirements.txt
python3 diagram.py        # → design_diagram.png
python3 build_ppt.py      # → exoplanet_data_quality_audit.pptx
```

Both scripts are idempotent — re-running overwrites existing outputs with identical results
given the same input data.

---

## Known Constraints

| Constraint | Detail |
|---|---|
| Transit bias | 96% of planets are transit-detected; completeness trends proxy method as well as recency |
| Snapshot data | `exoplanets.csv` is a point-in-time pull; recent planets will gain follow-up data over time |
| Year bin noise | Pre-2009 bins have <10 planets; Panel 2 completeness values are noisy in that region |
| pl_eqt_computed scope | Only `pl_eqt` has a computed flag; no other columns have an analogous reliability dimension in this dataset |
| 3 vs 4 worst offenders | DESIGN.md mentioned 4 columns for Panel 2; implementation uses 3 (`st_met`, `pl_orbsmax`, `sy_dist`) — `pl_orbper` was excluded as its missingness pattern is similar to `sy_dist` with less analytical impact |
