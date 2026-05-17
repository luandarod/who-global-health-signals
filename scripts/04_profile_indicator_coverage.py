"""Profile WHO GHO indicator coverage for candidate selection.

Run from the repository root:

    python scripts/04_profile_indicator_coverage.py

Input:
    data/interim/who_indicator_candidates.csv

Outputs:
    data/interim/who_indicator_coverage_profile.csv
    data/interim/who_indicator_shortlist.csv

The script downloads each candidate indicator, normalizes the frame and computes
coverage signals that help select a compact modeling dataset.
"""

from __future__ import annotations

from pathlib import Path
import sys
import time

import pandas as pd
import requests

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.data.who_client import WHOGHOClient, normalize_indicator_frame  # noqa: E402

INTERIM_DIR = PROJECT_ROOT / "data" / "interim"
CANDIDATES_PATH = INTERIM_DIR / "who_indicator_candidates.csv"
PROFILE_PATH = INTERIM_DIR / "who_indicator_coverage_profile.csv"
SHORTLIST_PATH = INTERIM_DIR / "who_indicator_shortlist.csv"

# Keep the first profiling run practical. We will expand after seeing which
# themes have the best coverage.
MAX_PER_THEME = 18
RECENT_YEAR_MIN = 2015
MIN_COUNTRIES = 90
MIN_RECENT_YEARS = 3

THEME_PRIORITY = {
    "outcome_life_expectancy": 0,
    "maternal_child_mortality": 1,
    "coverage_and_access": 2,
    "immunization": 3,
    "environment_sanitation": 4,
    "communicable_diseases": 5,
    "health_system_capacity": 6,
}


def select_candidates_for_profiling(candidates: pd.DataFrame) -> pd.DataFrame:
    """Limit candidates per theme so the first run is not too slow."""
    candidates = candidates.copy()
    candidates["theme_priority"] = candidates["theme"].map(THEME_PRIORITY).fillna(99)
    candidates = candidates.sort_values(["theme_priority", "theme", "indicator_name", "indicator_code"])
    return candidates.groupby("theme", group_keys=False).head(MAX_PER_THEME).reset_index(drop=True)


def profile_indicator(client: WHOGHOClient, row: pd.Series) -> dict[str, object]:
    code = str(row["indicator_code"])
    name = str(row["indicator_name"])
    theme = str(row["theme"])

    started = time.time()
    try:
        raw = client.indicator_data(code)
        frame = normalize_indicator_frame(raw)
        status = "ok"
        error = ""
    except (requests.RequestException, ValueError, TypeError) as exc:
        return {
            "theme": theme,
            "indicator_code": code,
            "indicator_name": name,
            "status": "error",
            "error": str(exc)[:300],
            "rows": 0,
            "countries": 0,
            "years": 0,
            "min_year": pd.NA,
            "max_year": pd.NA,
            "recent_years": 0,
            "recent_rows": 0,
            "sex_dimension_values": "",
            "elapsed_seconds": round(time.time() - started, 2),
        }

    if frame.empty:
        return {
            "theme": theme,
            "indicator_code": code,
            "indicator_name": name,
            "status": status,
            "error": error,
            "rows": 0,
            "countries": 0,
            "years": 0,
            "min_year": pd.NA,
            "max_year": pd.NA,
            "recent_years": 0,
            "recent_rows": 0,
            "sex_dimension_values": "",
            "elapsed_seconds": round(time.time() - started, 2),
        }

    years = frame["TimeDim"].dropna() if "TimeDim" in frame.columns else pd.Series(dtype="Int64")
    recent = frame.loc[frame["TimeDim"] >= RECENT_YEAR_MIN] if "TimeDim" in frame.columns else frame.iloc[0:0]

    countries = frame["SpatialDim"].nunique(dropna=True) if "SpatialDim" in frame.columns else 0
    recent_years = recent["TimeDim"].nunique(dropna=True) if "TimeDim" in recent.columns else 0
    recent_rows = len(recent)

    sex_values = ""
    if "Dim1" in frame.columns:
        unique_dim1 = sorted(str(value) for value in frame["Dim1"].dropna().unique()[:10])
        sex_values = " | ".join(unique_dim1)

    return {
        "theme": theme,
        "indicator_code": code,
        "indicator_name": name,
        "status": status,
        "error": error,
        "rows": len(frame),
        "countries": countries,
        "years": years.nunique(dropna=True),
        "min_year": int(years.min()) if not years.empty else pd.NA,
        "max_year": int(years.max()) if not years.empty else pd.NA,
        "recent_years": recent_years,
        "recent_rows": recent_rows,
        "sex_dimension_values": sex_values,
        "elapsed_seconds": round(time.time() - started, 2),
    }


def score_profile(profile: pd.DataFrame) -> pd.DataFrame:
    profile = profile.copy()
    profile["coverage_score"] = (
        profile["countries"].fillna(0).clip(upper=200) * 0.45
        + profile["recent_years"].fillna(0).clip(upper=15) * 5
        + profile["recent_rows"].fillna(0).clip(upper=3000) * 0.015
        + profile["years"].fillna(0).clip(upper=30) * 1.5
    )
    profile["passes_minimum"] = (
        (profile["status"] == "ok")
        & (profile["countries"] >= MIN_COUNTRIES)
        & (profile["recent_years"] >= MIN_RECENT_YEARS)
    )
    return profile.sort_values(["passes_minimum", "theme", "coverage_score"], ascending=[False, True, False])


def main() -> None:
    if not CANDIDATES_PATH.exists():
        raise SystemExit("Run scripts/03_discover_indicator_candidates.py first.")

    candidates = pd.read_csv(CANDIDATES_PATH)
    selected = select_candidates_for_profiling(candidates)
    print(f"Candidate rows available: {len(candidates):,}")
    print(f"Profiling selected candidates: {len(selected):,}")
    print(f"Max per theme: {MAX_PER_THEME}")

    client = WHOGHOClient()
    rows: list[dict[str, object]] = []

    for index, row in selected.iterrows():
        print(f"[{index + 1:03d}/{len(selected):03d}] {row['theme']} | {row['indicator_code']} | {row['indicator_name'][:85]}")
        rows.append(profile_indicator(client, row))

    profile = score_profile(pd.DataFrame(rows))
    profile.to_csv(PROFILE_PATH, index=False)

    shortlist = (
        profile.loc[profile["passes_minimum"]]
        .sort_values(["theme", "coverage_score"], ascending=[True, False])
        .groupby("theme", group_keys=False)
        .head(6)
        .reset_index(drop=True)
    )
    shortlist.to_csv(SHORTLIST_PATH, index=False)

    print("\nCoverage profile exported:", PROFILE_PATH.relative_to(PROJECT_ROOT))
    print("Shortlist exported:", SHORTLIST_PATH.relative_to(PROJECT_ROOT))
    print("\nProfile status count:")
    print(profile["status"].value_counts(dropna=False))
    print("\nShortlist count by theme:")
    if shortlist.empty:
        print("No indicators passed minimum coverage. Lower thresholds or inspect profile output.")
    else:
        print(shortlist["theme"].value_counts().sort_index())
        print("\nShortlist preview:")
        columns = [
            "theme",
            "indicator_code",
            "indicator_name",
            "countries",
            "years",
            "min_year",
            "max_year",
            "recent_years",
            "coverage_score",
        ]
        print(shortlist[columns].to_string(index=False))


if __name__ == "__main__":
    main()
