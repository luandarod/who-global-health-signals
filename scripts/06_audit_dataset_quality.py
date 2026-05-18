"""Audit missingness and create a cleaner modeling-ready dataset.

Run from the repository root:

    python scripts/06_audit_dataset_quality.py

Inputs:
    data/processed/who_country_year_dataset.csv
    data/interim/who_country_year_variable_dictionary.csv

Outputs:
    outputs/tables/dataset_overview.csv
    outputs/tables/variable_missingness.csv
    outputs/tables/year_coverage.csv
    outputs/tables/country_coverage.csv
    data/processed/who_country_year_modeling_ready.csv
    data/processed/who_country_year_modeling_ready.parquet

Why this exists:
    The raw analytical table is intentionally wide and sparse because WHO
    indicators have different time ranges, reporting patterns and dimensions.
    This script separates the exploratory dataset from a modeling-ready subset.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = PROJECT_ROOT / "data" / "processed" / "who_country_year_dataset.csv"
DICTIONARY_PATH = PROJECT_ROOT / "data" / "interim" / "who_country_year_variable_dictionary.csv"
OUTPUT_TABLES = PROJECT_ROOT / "outputs" / "tables"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

TARGET_COLUMN = "life_expectancy_at_birth"
ID_COLUMNS = {"country_code", "year", "region_code", "region"}
QUALITY_COLUMNS = {"available_indicator_count", "missing_indicator_count", "data_completeness_score"}

# Conservative defaults for the first modeling version.
MIN_YEAR = 2000
MIN_COMPLETENESS_SCORE = 0.25
MIN_VARIABLE_NON_NULL_SHARE = 0.35


def load_dataset() -> pd.DataFrame:
    if not DATASET_PATH.exists():
        raise SystemExit("Dataset not found. Run scripts/05_build_country_year_dataset.py first.")
    return pd.read_csv(DATASET_PATH)


def get_indicator_columns(dataset: pd.DataFrame) -> list[str]:
    excluded = ID_COLUMNS | QUALITY_COLUMNS
    return [col for col in dataset.columns if col not in excluded]


def build_missingness_table(dataset: pd.DataFrame, indicator_columns: list[str]) -> pd.DataFrame:
    rows = []
    total_rows = len(dataset)
    for column in indicator_columns:
        non_null = int(dataset[column].notna().sum())
        rows.append(
            {
                "variable_name": column,
                "non_null_rows": non_null,
                "missing_rows": int(dataset[column].isna().sum()),
                "non_null_share": non_null / total_rows if total_rows else 0,
                "missing_share": 1 - (non_null / total_rows if total_rows else 0),
            }
        )
    return pd.DataFrame(rows).sort_values("non_null_share", ascending=False)


def build_year_coverage(dataset: pd.DataFrame, indicator_columns: list[str]) -> pd.DataFrame:
    year_coverage = (
        dataset.groupby("year", dropna=False)
        .agg(
            rows=("country_code", "size"),
            countries=("country_code", "nunique"),
            mean_available_indicators=("available_indicator_count", "mean"),
            mean_completeness=("data_completeness_score", "mean"),
        )
        .reset_index()
        .sort_values("year")
    )
    if TARGET_COLUMN in indicator_columns:
        target_by_year = (
            dataset.loc[dataset[TARGET_COLUMN].notna()]
            .groupby("year")
            .agg(target_rows=(TARGET_COLUMN, "size"), target_countries=("country_code", "nunique"))
            .reset_index()
        )
        year_coverage = year_coverage.merge(target_by_year, on="year", how="left")
    return year_coverage


def build_country_coverage(dataset: pd.DataFrame) -> pd.DataFrame:
    return (
        dataset.groupby(["country_code", "region_code", "region"], dropna=False)
        .agg(
            years=("year", "nunique"),
            min_year=("year", "min"),
            max_year=("year", "max"),
            mean_available_indicators=("available_indicator_count", "mean"),
            mean_completeness=("data_completeness_score", "mean"),
        )
        .reset_index()
        .sort_values(["mean_completeness", "years"], ascending=[False, False])
    )


def filter_modeling_rows(dataset: pd.DataFrame) -> pd.DataFrame:
    if TARGET_COLUMN not in dataset.columns:
        raise SystemExit(f"Target column not found: {TARGET_COLUMN}")

    modeling = dataset.loc[dataset["year"] >= MIN_YEAR].copy()
    modeling = modeling.loc[modeling[TARGET_COLUMN].notna()].copy()

    if "data_completeness_score" in modeling.columns:
        modeling = modeling.loc[modeling["data_completeness_score"] >= MIN_COMPLETENESS_SCORE].copy()

    return modeling


def build_modeling_ready_dataset(dataset: pd.DataFrame, missingness: pd.DataFrame) -> pd.DataFrame:
    modeling = filter_modeling_rows(dataset)
    modeling_missingness = build_missingness_table(modeling, get_indicator_columns(modeling))

    keep_variables = modeling_missingness.loc[
        modeling_missingness["non_null_share"] >= MIN_VARIABLE_NON_NULL_SHARE,
        "variable_name",
    ].tolist()

    if TARGET_COLUMN not in keep_variables:
        keep_variables.insert(0, TARGET_COLUMN)

    keep_columns = [col for col in ["country_code", "year", "region_code", "region"] if col in dataset.columns]
    keep_columns += [col for col in keep_variables if col in dataset.columns]
    keep_columns += [col for col in QUALITY_COLUMNS if col in dataset.columns]

    modeling = modeling.loc[:, keep_columns].copy()
    modeling = modeling.sort_values(["country_code", "year"]).reset_index(drop=True)
    return modeling


def main() -> None:
    dataset = load_dataset()
    indicator_columns = get_indicator_columns(dataset)

    missingness = build_missingness_table(dataset, indicator_columns)
    year_coverage = build_year_coverage(dataset, indicator_columns)
    country_coverage = build_country_coverage(dataset)
    modeling_ready = build_modeling_ready_dataset(dataset, missingness)

    overview = pd.DataFrame(
        [
            {"metric": "rows", "value": len(dataset)},
            {"metric": "columns", "value": len(dataset.columns)},
            {"metric": "countries", "value": dataset["country_code"].nunique(dropna=True)},
            {"metric": "min_year", "value": dataset["year"].min()},
            {"metric": "max_year", "value": dataset["year"].max()},
            {"metric": "indicator_columns", "value": len(indicator_columns)},
            {"metric": "modeling_ready_rows", "value": len(modeling_ready)},
            {"metric": "modeling_ready_columns", "value": len(modeling_ready.columns)},
            {"metric": "modeling_min_year", "value": MIN_YEAR},
            {"metric": "modeling_min_completeness_score", "value": MIN_COMPLETENESS_SCORE},
            {"metric": "modeling_min_variable_non_null_share", "value": MIN_VARIABLE_NON_NULL_SHARE},
        ]
    )

    overview.to_csv(OUTPUT_TABLES / "dataset_overview.csv", index=False)
    missingness.to_csv(OUTPUT_TABLES / "variable_missingness.csv", index=False)
    year_coverage.to_csv(OUTPUT_TABLES / "year_coverage.csv", index=False)
    country_coverage.to_csv(OUTPUT_TABLES / "country_coverage.csv", index=False)
    modeling_ready.to_csv(PROCESSED_DIR / "who_country_year_modeling_ready.csv", index=False)
    modeling_ready.to_parquet(PROCESSED_DIR / "who_country_year_modeling_ready.parquet", index=False)

    print("Dataset quality audit completed.")
    print("\nOverview:")
    print(overview.to_string(index=False))
    print("\nTop variables by coverage:")
    print(missingness.head(15).to_string(index=False))
    print("\nModeling-ready dataset:")
    print(f"rows={len(modeling_ready):,} | cols={len(modeling_ready.columns):,}")
    print("\nFiles exported:")
    print("- outputs/tables/dataset_overview.csv")
    print("- outputs/tables/variable_missingness.csv")
    print("- outputs/tables/year_coverage.csv")
    print("- outputs/tables/country_coverage.csv")
    print("- data/processed/who_country_year_modeling_ready.csv")
    print("- data/processed/who_country_year_modeling_ready.parquet")


if __name__ == "__main__":
    main()
