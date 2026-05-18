"""Export compact assets for the final interactive report.

Run from the repository root:

    python scripts/11_export_report_assets.py

Inputs:
    data/processed/who_country_year_dataset.csv
    data/processed/who_country_year_modeling_ready.csv
    outputs/tables/model_comparison_metrics.csv
    outputs/tables/executive_findings.csv
    outputs/tables/residuals_by_country.csv
    outputs/tables/residuals_by_region.csv
    outputs/tables/residuals_by_year.csv
    outputs/tables/variable_missingness.csv

Outputs:
    data/public/report_summary.json
    data/public/model_comparison.json
    data/public/region_residuals.json
    data/public/year_residuals.json
    data/public/country_residuals_top.json
    data/public/life_expectancy_trends.json
    data/public/data_completeness_by_region.json
    data/public/variable_coverage.json

These JSON files are intentionally compact and frontend-friendly. They will feed
an Astro/Svelte scrollytelling report in the next project phase.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DIR = PROJECT_ROOT / "data" / "public"
TABLES_DIR = PROJECT_ROOT / "outputs" / "tables"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

PUBLIC_DIR.mkdir(parents=True, exist_ok=True)

FULL_DATASET_PATH = PROCESSED_DIR / "who_country_year_dataset.csv"
MODELING_DATASET_PATH = PROCESSED_DIR / "who_country_year_modeling_ready.csv"
MODEL_COMPARISON_PATH = TABLES_DIR / "model_comparison_metrics.csv"
EXECUTIVE_FINDINGS_PATH = TABLES_DIR / "executive_findings.csv"
RESIDUALS_COUNTRY_PATH = TABLES_DIR / "residuals_by_country.csv"
RESIDUALS_REGION_PATH = TABLES_DIR / "residuals_by_region.csv"
RESIDUALS_YEAR_PATH = TABLES_DIR / "residuals_by_year.csv"
VARIABLE_MISSINGNESS_PATH = TABLES_DIR / "variable_missingness.csv"

TARGET = "life_expectancy_at_birth"
TOP_COUNTRIES = 30


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise SystemExit(f"Required file not found: {path.relative_to(PROJECT_ROOT)}")
    return pd.read_csv(path)


def sanitize_json_value(value: Any) -> Any:
    """Convert pandas/numpy missing values into valid JSON nulls.

    Python's json.dump can otherwise write NaN, which is not valid JSON for
    browser JSON.parse/fetch parsing.
    """
    if value is None:
        return None
    if pd.isna(value):
        return None
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    if isinstance(value, dict):
        return {str(key): sanitize_json_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [sanitize_json_value(item) for item in value]
    return value


def clean_records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    records = frame.to_dict(orient="records")
    return sanitize_json_value(records)


def write_json(name: str, payload: Any) -> None:
    path = PUBLIC_DIR / name
    clean_payload = sanitize_json_value(payload)
    with path.open("w", encoding="utf-8") as file:
        json.dump(clean_payload, file, ensure_ascii=False, indent=2, allow_nan=False)
    print(f"Saved: {path.relative_to(PROJECT_ROOT)}")


def build_report_summary(full: pd.DataFrame, modeling: pd.DataFrame, executive: pd.DataFrame, comparison: pd.DataFrame) -> dict[str, Any]:
    best_model = comparison.sort_values("test_mae", ascending=True).iloc[0]
    summary = {
        "project_title": "Global Health Signals",
        "project_subtitle": "Predicting life expectancy from WHO health-system indicators using TabPFN",
        "analytical_question": "Can public health indicators from WHO explain and predict differences in life expectancy across countries?",
        "dataset": {
            "full_rows": int(len(full)),
            "full_columns": int(len(full.columns)),
            "countries": int(full["country_code"].nunique(dropna=True)),
            "min_year": int(full["year"].min()),
            "max_year": int(full["year"].max()),
            "modeling_rows": int(len(modeling)),
            "modeling_columns": int(len(modeling.columns)),
        },
        "best_model": {
            "name": str(best_model["model"]),
            "test_mae": float(best_model["test_mae"]),
            "test_rmse": float(best_model["test_rmse"]),
            "test_r2": float(best_model["test_r2"]),
        },
        "executive_findings": clean_records(executive),
        "chapters": [
            {
                "id": "data_foundation",
                "title": "The data foundation",
                "description": "WHO indicators are broad, historical and unevenly complete across countries and years.",
            },
            {
                "id": "health_signals",
                "title": "The health-system signals",
                "description": "Mortality, immunization and expenditure signals structure the predictive layer.",
            },
            {
                "id": "prediction_layer",
                "title": "The prediction layer",
                "description": "TabPFN predicted recent life expectancy with lower error than linear and tree baselines.",
            },
            {
                "id": "residual_intelligence",
                "title": "Residual intelligence",
                "description": "Outliers reveal countries performing better or worse than expected given the available signals.",
            },
        ],
    }
    return summary


def build_life_expectancy_trends(modeling: pd.DataFrame) -> pd.DataFrame:
    if TARGET not in modeling.columns:
        return pd.DataFrame()
    return (
        modeling.groupby(["year", "region"], dropna=False)
        .agg(life_expectancy=(TARGET, "mean"), countries=("country_code", "nunique"))
        .reset_index()
        .sort_values(["year", "region"])
    )


def build_completeness_by_region(full: pd.DataFrame) -> pd.DataFrame:
    return (
        full.loc[full["year"] >= 2000]
        .groupby("region", dropna=False)
        .agg(
            mean_completeness=("data_completeness_score", "mean"),
            countries=("country_code", "nunique"),
            rows=("country_code", "size"),
        )
        .reset_index()
        .sort_values("mean_completeness", ascending=False)
    )


def main() -> None:
    full = read_csv(FULL_DATASET_PATH)
    modeling = read_csv(MODELING_DATASET_PATH)
    comparison = read_csv(MODEL_COMPARISON_PATH)
    executive = read_csv(EXECUTIVE_FINDINGS_PATH)
    residuals_country = read_csv(RESIDUALS_COUNTRY_PATH)
    residuals_region = read_csv(RESIDUALS_REGION_PATH)
    residuals_year = read_csv(RESIDUALS_YEAR_PATH)
    missingness = read_csv(VARIABLE_MISSINGNESS_PATH)

    report_summary = build_report_summary(full, modeling, executive, comparison)
    life_trends = build_life_expectancy_trends(modeling)
    completeness_region = build_completeness_by_region(full)
    country_top = residuals_country.sort_values("mean_abs_error", ascending=False).head(TOP_COUNTRIES)
    coverage_top = missingness.sort_values("non_null_share", ascending=False).head(20)

    write_json("report_summary.json", report_summary)
    write_json("model_comparison.json", clean_records(comparison))
    write_json("region_residuals.json", clean_records(residuals_region))
    write_json("year_residuals.json", clean_records(residuals_year))
    write_json("country_residuals_top.json", clean_records(country_top))
    write_json("life_expectancy_trends.json", clean_records(life_trends))
    write_json("data_completeness_by_region.json", clean_records(completeness_region))
    write_json("variable_coverage.json", clean_records(coverage_top))

    print("\nReport asset export completed.")
    print("Next step: build the interactive report shell and consume these JSON files.")


if __name__ == "__main__":
    main()
