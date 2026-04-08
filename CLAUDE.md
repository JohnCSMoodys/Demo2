# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

This is a design-first data visualization exercise. The primary artifact is `DESIGN.md` — produced before any code is written. The dataset is NASA exoplanet catalog data used as a vehicle for practicing design thinking and human-agent collaboration.

## Repository State

- `exoplanets.csv` — 1,173 exoplanet records, 19 columns (see `exoplanets_data_dictionary.csv` for schema)
- `exoplanets_data_dictionary.csv` — column definitions and units
- `DESIGN.md` — the completed design artifact (goal, audience, hypothesis, viz choice, text diagram, risks)
- `diagram.py` — generates `design_diagram.png` (two-panel matplotlib figure)
- `build_ppt.py` — generates `exoplanet_data_quality_audit.pptx` (7-slide deck)
- `requirements.txt` — pinned dependencies (matplotlib, pandas, numpy, python-pptx)

## Design Decisions Already Made

The design phase is complete. Do not revisit these unless the user explicitly asks to reopen them:

- **Audience:** Data practitioner (assumes familiarity with missingness, derived features, selection bias)
- **Story:** Completeness is uneven and systematic — expensive columns sparse (A), some values derived not measured (B), recent bulk discoveries shallower (C)
- **Visualization:** Two-panel layout — column completeness profile (Panel 1) + completeness over time for worst-offender columns (Panel 2)
- **Key columns:** `st_met`, `pl_orbsmax`, `sy_dist`, `pl_eqt`/`pl_eqt_computed`, `disc_year`

## Working Conventions

**Design before code.** If the user asks to implement, first confirm `DESIGN.md` is stable. The README treats it as a required checkpoint.

**Stay in the current phase.** If implementation has not started, do not choose libraries, write code, or plan technical architecture unless asked.

**Offer alternatives before converging.** When proposing a direction, show 2-3 options with trade-offs. Do not assume the first suggestion is the right one.

**Restate the goal before proposing.** Before making a significant design proposal, restate the goal in your own words so the user can catch misalignment early.

**Push back when something seems off.** Silent compliance is the failure mode here (see README: "Compliance Bias"). If a request seems to contradict the established design or will produce a misleading visualization, say so.

## Known Risks (from DESIGN.md)

- Pre-2009 year bins have <10 planets — percentages are noisy; annotate or bin early years
- `pl_eqt_computed` means derived, not wrong — frame as a reliability flag, not an error flag
- `st_met` 7% missingness may be a pipeline artifact; flag for investigation before use as a feature
- Transit method dominates (96%); year-level completeness trends may proxy method, not recency
