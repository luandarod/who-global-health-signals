"""Discover candidate WHO GHO indicators for the first analytical dataset.

Run from the repository root:

    python scripts/03_discover_indicator_candidates.py

The script searches the WHO indicator catalog by thematic keyword rules and
exports a cleaner candidate table to data/interim/who_indicator_candidates.csv.
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

THEME_PATTERNS: dict[str, list[str]] = {
    "outcome_life_expectancy": [
        r"\blife expectancy\b",
        r"\bhealthy life expectancy\b",
    ],
    "maternal_child_mortality": [
        r"\bmaternal mortality\b",
        r"\bneonatal mortality\b",
        r"\binfant mortality\b",
        r"\bunder five mortality\b",
        r"\bunder 5 mortality\b",
        r"\bchild mortality\b",
    ],
    "coverage_and_access": [
        r"\buniversal health coverage\b",
        r"\buhc\b",
        r"\bservice coverage\b",
        r"\bskilled birth\b",
        r"\bantenatal care\b",
        r"\bessential health services\b",
    ],
    "immunization": [
        r"\bimmunization\b",
        r"\bimmunisation\b",
        r"\bvaccination\b",
        r"\bvaccine\b",
        r"\bmeasles\b",
        r"\bdiphtheria\b",
        r"\bdtp3\b",
    ],
    "environment_sanitation": [
        r"\bsanitation\b",
        r"\bdrinking water\b",
        r"\bwash\b",
        r"\bair pollution\b",
        r"\bambient air\b",
        r"\bhousehold air\b",
        r"\bclean fuels\b",
    ],
    "communicable_diseases": [
        r"\btuberculosis\b",
        r"\btb incidence\b",
        r"\bhiv\b",
        r"\bmalaria\b",
    ],
    "health_system_capacity": [
        r"\bhealth workforce\b",
        r"\bphysicians\b",
        r"\bmedical doctors\b",
        r"\bnursing\b",
        r"\bhospital beds\b",
        r"\bhealth expenditure\b",
    ],
}

EXCLUDE_PATTERNS = [
    r"\barchived\b",
    r"\balcohol\b",
    r"\btobacco\b",
    r"\bsuicide\b",
    r"\broads? traffic\b",
    r"\bviolence\b",
]


def normalize_text(value: object) -> str:
    text = "" if pd.isna(value) else str(value)
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def is_excluded(text: str) -> bool:
    return any(re.search(pattern, text) for pattern in EXCLUDE_PATTERNS)


def main() -> None:
    client = WHOGHOClient()
    indicators = client.indicators().copy()

    print(f"Indicator catalog loaded: {len(indicators):,} rows")
    print("Columns:", indicators.columns.tolist())

    code_column = "IndicatorCode" if "IndicatorCode" in indicators.columns else indicators.columns[0]
    name_column = "IndicatorName" if "IndicatorName" in indicators.columns else indicators.columns[-1]

    indicators["_indicator_name_norm"] = indicators[name_column].map(normalize_text)
    indicators["_indicator_code_norm"] = indicators[code_column].map(normalize_text)

    # Search only the human-readable indicator name. Searching the code creates
    # false positives, for example HIV inside ARCHIVED code suffixes.
    searchable = indicators.loc[~indicators["_indicator_name_norm"].map(is_excluded)].copy()

    rows: list[dict[str, object]] = []
    seen: set[tuple[str, str]] = set()

    for theme, patterns in THEME_PATTERNS.items():
        for pattern in patterns:
            mask = searchable["_indicator_name_norm"].str.contains(pattern, regex=True, na=False)
            matches = searchable.loc[mask].copy()
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
                        "matched_pattern": pattern,
                        "indicator_code": code,
                        "indicator_name": name,
                    }
                )

    candidates = pd.DataFrame(rows)
    if candidates.empty:
        raise SystemExit("No indicator candidates found. Inspect catalog column names and pattern list.")

    candidates = candidates.sort_values(["theme", "indicator_name", "indicator_code"]).reset_index(drop=True)
    output_path = INTERIM_DIR / "who_indicator_candidates.csv"
    candidates.to_csv(output_path, index=False)

    print(f"Candidate indicators exported: {output_path.relative_to(PROJECT_ROOT)}")
    print(f"Rows: {len(candidates):,}")
    print("\nCandidate count by theme:")
    print(candidates["theme"].value_counts().sort_index())
    print("\nPreview:")
    print(candidates.head(50).to_string(index=False))


if __name__ == "__main__":
    main()
