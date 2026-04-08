"""
Phase 1 — Data Preparation
Computes the three metric sets that feed Panel 1 and Panel 2.
"""

import pandas as pd

PROFILE_COLS = [
    "st_met", "pl_orbsmax", "sy_dist", "pl_orbper",
    "st_teff", "st_rad", "st_mass", "pl_bmasse", "pl_rade",
]

WATCH_COLS = ["st_met", "pl_orbsmax", "sy_dist"]


def load(path="exoplanets.csv"):
    df = pd.read_csv(path)
    n = len(df)

    # Per-column missingness / presence
    missing_pct = {c: df[c].isna().sum() / n * 100 for c in PROFILE_COLS}
    present_pct = {c: 100 - missing_pct[c] for c in PROFILE_COLS}

    # pl_eqt: three-way split
    eqt_missing  = df["pl_eqt"].isna().sum() / n * 100
    eqt_computed = df["pl_eqt_computed"].sum() / n * 100
    eqt_measured = 100 - eqt_missing - eqt_computed

    # Per-year completeness (years with ≥ 5 planets)
    year_counts = df["disc_year"].value_counts()
    valid_years = sorted(
        [y for y in df["disc_year"].dropna().unique() if year_counts[y] >= 5]
    )
    completeness_by_year = {
        c: [(1 - df[df["disc_year"] == y][c].isna().mean()) * 100 for y in valid_years]
        for c in WATCH_COLS
    }

    return dict(
        df=df,
        n=n,
        missing_pct=missing_pct,
        present_pct=present_pct,
        eqt_missing=eqt_missing,
        eqt_computed=eqt_computed,
        eqt_measured=eqt_measured,
        valid_years=valid_years,
        completeness_by_year=completeness_by_year,
    )


def verify(data):
    missing_pct        = data["missing_pct"]
    eqt_measured       = data["eqt_measured"]
    eqt_computed       = data["eqt_computed"]
    eqt_missing        = data["eqt_missing"]
    valid_years        = data["valid_years"]
    completeness_by_year = data["completeness_by_year"]

    errors = []

    # st_met is the worst-missing column
    if not (abs(missing_pct["st_met"] - 7) < 3):
        errors.append(f"st_met missing_pct={missing_pct['st_met']:.2f}% — expected ≈7%")
    if missing_pct["st_met"] != max(missing_pct.values()):
        errors.append("st_met is not the highest-missing column")

    # pl_eqt split sums to 100
    total = eqt_measured + eqt_computed + eqt_missing
    if abs(total - 100.0) > 1e-6:
        errors.append(f"eqt split sums to {total:.8f}, expected 100.0")

    # valid_years starts no earlier than 2002 (2004 has exactly 5 — hits the ≥5 threshold)
    if valid_years[0] < 2002:
        errors.append(f"valid_years starts at {valid_years[0]}, expected ≥ 2002")

    # All completeness values in [0, 100]
    all_vals = [v for vals in completeness_by_year.values() for v in vals]
    out_of_range = [v for v in all_vals if v < 0 or v > 100]
    if out_of_range:
        errors.append(f"{len(out_of_range)} completeness values outside [0, 100]: {out_of_range[:3]}")

    return errors


if __name__ == "__main__":
    data = load()
    errors = verify(data)
    if errors:
        for e in errors:
            print(f"FAIL  {e}")
    else:
        mp = data["missing_pct"]
        print(f"PASS  st_met missing_pct          = {mp['st_met']:.2f}%  (worst offender)")
        print(f"PASS  eqt split sums to 100        = {data['eqt_measured']:.2f} + {data['eqt_computed']:.2f} + {data['eqt_missing']:.2f}")
        print(f"PASS  valid_years starts at         {data['valid_years'][0]:.0f}")
        all_vals = [v for vals in data["completeness_by_year"].values() for v in vals]
        print(f"PASS  completeness range            [{min(all_vals):.1f}, {max(all_vals):.1f}]")
