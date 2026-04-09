# DESIGN.md — Stars Data Quality Audit

## Goal

Produce a data quality audit visualization that helps a practitioner understand where this
dataset is trustworthy, where it is thin, and where values are missing systematically —
before they begin any modeling or analysis.

## Audience

**Data practitioner.** Assumes familiarity with concepts like missingness, derived features,
and selection bias. Does not need domain astronomy knowledge. Wants calibrated trust in the
dataset, not a science story.

## Story Hypothesis

> Completeness in this catalog is uneven and concentrated: a single column (`metallicity_fe_h`)
> accounts for nearly all missingness, and the stars missing that column are not randomly
> distributed — they are data-sparse across the board, with dramatically elevated missingness
> in every other analytical field.

Three sub-claims:

- **A. Missingness is concentrated in metallicity** — `metallicity_fe_h` is missing 6.2% of
  the time vs. <2% for all other analytical columns. The gap reflects measurement cost:
  metallicity requires high-resolution spectroscopy while temperature, mass, and radius can
  be estimated photometrically or from stellar models.

- **B. Missing metallicity predicts missing everything else** — Stars without metallicity show
  dramatically elevated missingness across all other columns: `teff_k` is missing 25% of the
  time in that group (vs. 0.1% otherwise), `radius_solar` 11.7% (vs. 0.2%), `distance_pc`
  10.0% (vs. 0.7%), and `mass_solar` 6.7% (vs. 0.2%). These are not random gaps; they mark
  a distinct population of minimally-characterized stars.

- **C. Distance does not explain it** — Median distance for stars with vs. without metallicity
  is nearly identical (~255 pc vs. ~290 pc), ruling out observational depth or catalog depth
  as the primary driver. The gap is about which stars received spectroscopic follow-up, not
  how far away they are.

## Alternatives Considered

| Direction | Core question | Why not chosen |
|---|---|---|
| **Completeness vs. distance** | Do farther stars have worse data? | Tested: distance quartiles show uniform ~5.8% metallicity missingness at every range — no gradient |
| **Completeness vs. num_planets** | Do multi-planet systems have better data? | Bins above 3 planets are too small (n<40) for reliable percentages; no clear pattern |
| **Property distributions** | How do temperature, mass, and radius relate? | Exploratory/analytical, not a quality story; assumes data is already trusted |
| **Data quality audit** *(chosen)* | Where is data missing and who is missing it? | Directly answers "can I trust this?" before any downstream work |

## Visualization Choice

**Two-panel layout: Column Profile + Co-Missingness Decomposition**

- **Panel 1 (Column Completeness Profile):** Horizontal bar chart, one bar per analytically
  important column. Each bar shows % complete (filled) vs. % missing (empty). Sorted
  worst-to-best completeness. Covers sub-claim A.

- **Panel 2 (Conditional Missingness):** Grouped bar chart. X-axis = analytical columns
  (`teff_k`, `mass_solar`, `radius_solar`, `distance_pc`). For each column, two bars:
  missingness rate when `metallicity_fe_h` is present vs. missing. Annotated with the
  raw n (60 stars missing metallicity, 912 with it). Covers sub-claims B and C.

Why this over alternatives:
- A missingness matrix (rows = stars) is too dense at 972 rows and obscures the column-level story
- Panel 2 as a time series doesn't apply — no discovery year in this dataset
- The conditional missingness view makes the 25x–250x co-missingness gaps legible at a glance

## Key Columns

| Column | Role in viz | Why included |
|---|---|---|
| `metallicity_fe_h` | Worst offender in Panel 1; grouping variable in Panel 2 | 6.2% missing — 4x higher than nearest peer |
| `teff_k` | Panel 1 + Panel 2 (secondary column) | 1.6% overall; 25% when metallicity missing |
| `distance_pc` | Panel 1 + Panel 2 (secondary column) | 1.2% overall; 10% when metallicity missing; also tests C |
| `radius_solar` | Panel 1 + Panel 2 (secondary column) | 0.9% overall; 11.7% when metallicity missing |
| `mass_solar` | Panel 1 + Panel 2 (secondary column) | 0.6% overall; 6.7% when metallicity missing |
| `num_planets` | Context annotation only | 0% missing; shows these stars still have planet data |

**Left out:** `star_id`, `star_name`, `ra_deg`, `dec_deg` — identifier/positional columns with
zero missingness, not analytically risky.

## Text Diagram

```
PANEL 1 — Column Completeness Profile
(sorted worst to best; bars show share of 972 records)

metallicity_fe_h  ████████████████████████████████████████████░░░  93.8% complete
teff_k            ████████████████████████████████████████████████  98.4% complete
distance_pc       ████████████████████████████████████████████████  98.8% complete
radius_solar      ████████████████████████████████████████████████  99.1% complete
mass_solar        ████████████████████████████████████████████████  99.4% complete

  Legend: ████ present   ░░░░ missing


PANEL 2 — Conditional Missingness (when metallicity_fe_h is missing vs. present)

% missing
  25% |                 ██
      |                 ██
      |                 ██
  10% |                 ██         ░░        ░░
      |                 ██         ██        ░░
   5% |                 ██         ██        ██        ░░
      |  0.1% 6.7%      ██  0.2%   ██  0.2%  ██  0.7%  ██
   0% | ░░ ██         ░░ ██       ░░ ██      ░░ ██
      +─────────────────────────────────────────────────
         teff_k      mass_solar  radius_solar  distance_pc

  ██ metallicity missing (n=60)   ░░ metallicity present (n=912)

  Note: distance similar for both groups (median: 255 pc present, 290 pc missing)
  → distance is not the driver; these are data-sparse stars across the board
```

## Risks and Caveats

| Risk | Description | Mitigation |
|---|---|---|
| **Small group size** | Only 60 stars (6.2%) lack metallicity; conditional rates may be noisy | Show n on Panel 2; note confidence interval or flag as illustrative |
| **Causality direction** | Missing metallicity may be a symptom of data sparsity, not the cause — some third factor (observation program, survey type) may drive both | Frame as "co-missingness", not "metallicity causes other gaps" |
| **`metallicity_fe_h` outlier status** | 6.2% vs. <2% for peers is striking — could be a data pipeline artifact | Flag as "investigate before using as feature" rather than "don't use" |
| **`num_planets` completeness masks planet-data gaps** | This dataset only tracks star-level fields; planet-level data quality is not captured here | Note that this audit covers stellar columns only |
| **Snapshot in time** | Stars currently missing metallicity may gain measurements as surveys continue | Note dataset pull date; caveat that completeness will improve |

## What's Next

This design feeds directly into the Plan + Implement module:

1. Compute per-column missingness rates from `stars.csv`
2. Compute conditional missingness rates: for each column, % missing when `metallicity_fe_h`
   is absent vs. present
3. Build Panel 1 (horizontal bar chart, sorted worst-to-best)
4. Build Panel 2 (grouped bar chart, metallicity-missing vs. metallicity-present groups)
5. Compose into two-panel layout with shared title and annotations

No implementation decisions (library, format, interactivity) are locked in this document.
