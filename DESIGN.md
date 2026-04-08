# DESIGN.md — Exoplanet Data Quality Audit

## Goal

Produce a data quality audit visualization that helps a practitioner understand where this
dataset is trustworthy, where it is thin, and where values are derived rather than directly
observed — before they begin any modeling or analysis.

## Audience

**Data practitioner.** Assumes familiarity with concepts like missingness, derived features,
and selection bias. Does not need domain astronomy knowledge. Wants calibrated trust in the
dataset, not a science story.

## Story Hypothesis

> Completeness in this catalog is uneven and systematic: the most expensive columns to measure
> are the most sparsely filled, some values are derived from models rather than observed, and
> recent bulk discoveries are shallower than older ones.

Three sub-claims:

- **A. Missingness is structured** — Stellar metallicity (`st_met`) is missing ~7% of the time
  vs. <1% for other stellar columns. Cost of measurement (spectrometry vs. photometry) shapes
  the gaps, not randomness.

- **B. Measured ≠ computed** — `pl_eqt_computed` flags equilibrium temperatures derived from
  stellar models. A practitioner using temperature as a feature needs to know this distinction
  exists and how prevalent it is.

- **C. Completeness degrades with recency** — Discovery rate jumped from single digits (pre-2009)
  to 100+/year (2023–2025). High-volume survey planets likely have less follow-up data than
  earlier discoveries.

## Alternatives Considered

| Direction | Core question | Why not chosen |
|---|---|---|
| **Selection bias** | Why does transit dominate at 96%? What planets are we missing? | Interesting, but requires domain knowledge to interpret; less actionable for a practitioner starting an analysis |
| **Property relationships** | How do radius, mass, temperature, and orbital distance relate? | Exploratory/analytical, not a quality story; assumes data is already trusted |
| **Data quality audit** *(chosen)* | Where is data missing, derived, or unreliable? | Directly answers "can I trust this?" before any downstream work |

## Visualization Choice

**Two-panel layout: Column Profile + Time Decomposition**

- **Panel 1 (Column Completeness Profile):** Horizontal bar chart, one bar per analytically
  important column. Each bar is segmented: `measured` (solid) / `computed` (hatched) /
  `missing` (empty). Sorted worst-to-best. Covers sub-claims A and B.

- **Panel 2 (Completeness Over Time):** Line chart or heat strip, x-axis = discovery year,
  y-axis = % complete per year, one line per "worst offender" column. Annotated with
  Kepler launch (2009) and TESS launch (2018) as structural breaks. Covers sub-claim C.

Why this over alternatives:
- A missingness matrix (rows = planets) is too dense at 1,173 rows and obscures the column-level story
- A timeline-only view buries the column-level quality differences
- This layout lets Panel 1 give the summary and Panel 2 explain the cause for the worst columns

## Key Columns

| Column | Role in viz | Why included |
|---|---|---|
| `st_met` | Worst offender in Panel 1 + Panel 2 | 7% missing — stands out against <1% peers |
| `pl_orbsmax` | Second worst in Panel 1 + Panel 2 | ~3% missing; orbital geometry is analytically important |
| `sy_dist` | Panel 1 + Panel 2 | ~1.5% missing; used in spatial analysis |
| `pl_eqt` + `pl_eqt_computed` | Panel 1 (split bar) | Uniquely illustrates the measured vs. computed distinction |
| `disc_year` | Panel 2 x-axis | Temporal backbone for recency degradation story |
| `discoverymethod` | Annotation context only | Transit dominance (96%) is backdrop; not a primary axis |

**Left out:** `pl_name`, `hostname`, `star_id`, `ra`, `dec` — identifier/positional columns with
near-perfect completeness, not analytically risky.

## Text Diagram

```
PANEL 1 — Column Completeness Profile
(sorted worst to best; bars show share of 1,173 records)

st_met       ████████████████████████████████████████░░░░░░░  93.0% complete
pl_orbsmax   ███████████████████████████████████████████████  96.6% complete
sy_dist      ████████████████████████████████████████████████ 98.5% complete
pl_eqt       ██████████████████████ measured ███████ computed  ~100% (split)
pl_orbper    ████████████████████████████████████████████████ 98.9% complete
st_teff      ████████████████████████████████████████████████ 98.0% complete
st_rad       ████████████████████████████████████████████████ 99.1% complete
st_mass      ████████████████████████████████████████████████ 99.4% complete

  Legend: ████ measured   ████ computed (derived)   ░░░░ missing


PANEL 2 — Completeness Over Time (worst offenders by column)

% complete
  100% |  · · · · · · · · · · · · · · · · · ·─────────  st_rad / st_mass
       |  · · · · · · · · · · · · · ·────────────────── sy_dist
       |  · · · · · ·──────────────────────────────────  pl_orbsmax
   90% |
       |   ·  ·  ·  ──────────────────────────────────  st_met
   80% |
       |
        ──────────────────────────────────────────────▶ disc_year
       2002  2005   2009          2018          2025
                      ↑              ↑
                   Kepler         TESS
                  launch         launch

  (Each point = % of planets discovered that year with non-null value)
  st_met line stays lowest throughout; all columns dip after TESS ramp-up (2020+)
```

## Risks and Caveats

| Risk | Description | Mitigation |
|---|---|---|
| **Small year bins** | Pre-2009 has <10 planets/year; percentages will be noisy | Annotate or bin early years; note sample size |
| **`pl_eqt_computed` interpretation** | "Computed" ≠ "wrong" — derived temperatures can be accurate | Add callout: this is a reliability flag, not an error flag |
| **Recency signal may be misleading** | Recent planets may gain follow-up data over time; snapshot in time | Note dataset pull date; caveat that completeness will improve |
| **Transit bias as confound** | 96% transit-detected planets; missingness may correlate with method, not just recency | Worth testing in Panel 2 — if method is the driver, year is a proxy |
| **st_met outlier status** | 7% vs. <1% for peers is striking — could be a data pipeline artifact, not just cost | Flag as "investigate before using as feature" rather than "don't use" |

## What's Next

This design feeds directly into the Plan + Implement module:

1. Compute per-column missingness rates and `pl_eqt_computed` split from `exoplanets.csv`
2. Compute per-year completeness rates for the 4 worst-offender columns
3. Build Panel 1 (horizontal segmented bar chart)
4. Build Panel 2 (line chart with Kepler/TESS annotations)
5. Compose into two-panel layout with shared title and legend

No implementation decisions (library, format, interactivity) are locked in this document.
