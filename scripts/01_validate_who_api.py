"""Validate WHO GHO OData API access and inspect the target indicator.

Run from the repository root:

    python scripts/01_validate_who_api.py

The script checks:
1. Whether the WHO GHO API is reachable.
2. Whether the indicator catalog can be read.
3. Whether the target life expectancy indicator returns data.
4. Which columns are returned for the first sample.

Generated files are saved under data/raw/ and ignored by Git.
"""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.data.indicators import TARGET_INDICATOR  # noqa: E402
from src.data.who_client import WHOGHOClient, normalize_indicator_frame  # noqa: E402

RAW_DIR = PROJECT_ROOT / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)


def save_preview(frame: pd.DataFrame, name: str) -> None:
    path = RAW_DIR / name
    frame.to_csv(path, index=False)
    print(f"Saved: {path.relative_to(PROJECT_ROOT)} | rows={len(frame):,} | cols={len(frame.columns):,}")


def main() -> None:
    client = WHOGHOClient()

    print("1) Reading WHO indicator catalog...")
    indicators = client.indicators()
    print(f"Indicator catalog loaded: {len(indicators):,} rows")
    save_preview(indicators.head(100), "who_indicator_catalog_preview.csv")

    print("\n2) Reading WHO dimensions catalog...")
    dimensions = client.dimensions()
    print(f"Dimensions catalog loaded: {len(dimensions):,} rows")
    save_preview(dimensions.head(100), "who_dimensions_preview.csv")

    print(f"\n3) Reading target indicator: {TARGET_INDICATOR}...")
    raw_target = client.indicator_data(TARGET_INDICATOR, top=2500)
    target = normalize_indicator_frame(raw_target)
    print(f"Target sample loaded: {len(target):,} rows")
    print("Columns:")
    for column in target.columns:
        print(f"- {column}")

    save_preview(target, f"{TARGET_INDICATOR}_sample.csv")

    if "TimeDim" in target.columns:
        print("\nYear coverage in sample:")
        print(target["TimeDim"].value_counts().sort_index().tail(20))

    if "SpatialDim" in target.columns:
        print("\nCountry/entity count in sample:")
        print(target["SpatialDim"].nunique(dropna=True))

    print("\nWHO API validation completed.")


if __name__ == "__main__":
    main()
