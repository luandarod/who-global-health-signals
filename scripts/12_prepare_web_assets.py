"""Copy compact report JSON files into the web app public folder.

Run from the repository root after scripts/11_export_report_assets.py:

    python scripts/12_prepare_web_assets.py

Input:
    data/public/*.json

Output:
    web/public/data/*.json

The web report reads JSON files from /data/*.json at runtime.
"""

from __future__ import annotations

import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = PROJECT_ROOT / "data" / "public"
TARGET_DIR = PROJECT_ROOT / "web" / "public" / "data"

REQUIRED_FILES = [
    "report_summary.json",
    "model_comparison.json",
    "region_residuals.json",
    "year_residuals.json",
    "country_residuals_top.json",
    "life_expectancy_trends.json",
    "data_completeness_by_region.json",
    "variable_coverage.json",
]


def main() -> None:
    if not SOURCE_DIR.exists():
        raise SystemExit("data/public does not exist. Run scripts/11_export_report_assets.py first.")

    TARGET_DIR.mkdir(parents=True, exist_ok=True)

    missing = [name for name in REQUIRED_FILES if not (SOURCE_DIR / name).exists()]
    if missing:
        raise SystemExit(f"Missing report assets: {missing}. Run scripts/11_export_report_assets.py first.")

    for name in REQUIRED_FILES:
        source = SOURCE_DIR / name
        target = TARGET_DIR / name
        shutil.copy2(source, target)
        print(f"Copied: {source.relative_to(PROJECT_ROOT)} -> {target.relative_to(PROJECT_ROOT)}")

    print("\nWeb assets prepared.")
    print("Next: cd web && npm install && npm run dev")


if __name__ == "__main__":
    main()
