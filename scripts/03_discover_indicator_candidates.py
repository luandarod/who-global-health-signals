"""Discover candidate WHO GHO indicators for the first analytical dataset.

Run from the repository root:

    python scripts/03_discover_indicator_candidates.py

The script searches the WHO indicator catalog by thematic keywords and exports
a ranked candidate table to data/interim/who_indicator_candidates.csv.
"""

from __future__ import annotations

from pathlib import Path
import re
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.data.who_client import WHOGHOClient  # noqa: E402

INTERIM_DIR = PROJECT_ROOT / "data" / "interim"
INTERIM_DIR.mkdir(parents=True, exist_ok=True)

THEME_KEYWORDS: dict[str, list[str]] = {
    "outcome_life_expectancy": [
        "life expectancy",
        "healthy life expectancy",
    ],
    "maternal_child_mortality": [
        "maternal mortality",
        "neonatal mortality",
        "infant mortality",
        "under-five mortality",
        "under 5 mortality",
        "child mortality",
    ],
    "coverage_and_access": [
        "universal health coverage",
        "uhc",
        "service coverage",
        "skilled birth",
        "antenatal care",
        "essential health services",
    ],
    "immunization": [
        "immunization",
        "immunisation",
        "vaccination",
        "vaccine",
        "measles",
        "diphtheria",
        "dtp3",
    ],
    "environment_sanitation": [
        "sanitation",
        "drinking-water",
        "drinking water",
        "wash",
        "air pollution",
        "ambient air",
        "household air",
        "clean fuels",
    ],
    "communicable_diseases": [
        "tuberculosis",
        "tb incidence",
        "hiv",
        "malaria",
    ],
    "health_system_capacity": [
        "health workforce",
        "physicians",
        "nursing",
        "hospital beds",
        "health expenditure",
    ],
}


def normalize_text(value: object) -> str:
    text = "" if pd.isna(value) else str(value)
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def main() -> None:
    client = WHOGHOClient()
    indicators = client.indicators().copy()

    print(f"Indicator catalog loaded: {len(indicators):,} rows")
    print("Columns:", indicators.columns.tolist())

    code_column = "IndicatorCode" if "IndicatorCode" in indicators.columns else indicators.columns[0]
    name_column = "IndicatorName" if "IndicatorName" in indicators.columns else indicators.columns[-1]

    # The WHO catalog commonly returns IndicatorCode, IndicatorName and Language.
    # The fallback above keeps the script usable if the API changes column labels.
    indicators["_search_text"] = indicators.apply(
        lambda row: normalize_text(" ".join(str(row.get(col, "")) for col in indicators.columns)),
        axis=1,
    )

    rows: list[dict[str, object]] = []
    seen: set[tuple[str, str]] = set()

    for theme, keywords in THEME_KEYWORDS.items():
        for keyword in keywords:
            normalized_keyword = normalize_text(keyword)
            mask = indicators["_search_text"].str.contains(re.escape(normalized_keyword), na=False)
            matches = indicators.loc[mask].copy()
            for _, row in matches.iterrows():
                code = str(row.get(code_column, ""))
                name = str(row.get(name_column, ""))
                key = (theme, code)
                if key in seen:
                    continue
                seen.add(key)
                rows.append(
                    {
                        "theme": theme,
                        "matched_keyword": keyword,
                        "indicator_code": code,
                        "indicator_name": name,
                    }
                )

    candidates = pd.DataFrame(rows)
    if candidates.empty:
        raise SystemExit("No indicator candidates found. Inspect catalog column names and keyword list.")

    candidates = candidates.sort_values(["theme", "indicator_name", "indicator_code"]).reset_index(drop=True)
    output_path = INTERIM_DIR / "who_indicator_candidates.csv"
    candidates.to_csv(output_path, index=False)

    print(f"Candidate indicators exported: {output_path.relative_to(PROJECT_ROOT)}")
    print(f"Rows: {len(candidates):,}")
    print("\nCandidate count by theme:")
    print(candidates["theme"].value_counts().sort_index())
    print("\nPreview:")
    print(candidates.head(30).to_string(index=False))


if __name__ == "__main__":
    main()
