"""Build the first WHO country-year analytical dataset.

Run from the repository root:

    python scripts/05_build_country_year_dataset.py

Input:
    data/interim/who_indicator_shortlist.csv

Outputs:
    data/processed/who_country_year_dataset.csv
    data/processed/who_country_year_dataset.parquet
    data/interim/who_country_year_variable_dictionary.csv

This script downloads the shortlisted indicators, normalizes each indicator to
country-year format and pivots everything into one analytical table.
"""

from __future__ import annotations

from pathlib import Path
import re
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.data.indicators import TARGET_INDICATOR  # noqa: E402
from src.data.who_client import WHOGHOClient, normalize_indicator_frame  # noqa: E402

INTERIM_DIR = PROJECT_ROOT / "data" / "interim"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

SHORTLIST_PATH = INTERIM_DIR / "who_indicator_shortlist.csv"
DATASET_CSV_PATH = PROCESSED_DIR / "who_country_year_dataset.csv"
DATASET_PARQUET_PATH = PROCESSED_DIR / "who_country_year_dataset.parquet"
DICTIONARY_PATH = INTERIM_DIR / "who_country_year_variable_dictionary.csv"

COUNTRY_SPATIAL_TYPES = {"COUNTRY", "COUNTRY_AREA", "COUNTRY_GRP"}
PREFERRED_DIM1_VALUES = {"BTSX", "SEX_BTSX", "Both sexes", "Both sexes combined", "Total", "ALL"}
VARIABLE_NAME_MAX_LENGTH = 72
DIMENSION_VALUE_COLUMNS = ["Dim1", "Dim2", "Dim3", "Dim4"]


def slugify(value: str, max_length: int | None = None) -> str:
    text = value.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    if not text:
        return "indicator"
    if max_length is None:
        return text
    return text[:max_length].strip("_")


def make_unique_variable_name(indicator_name: str, indicator_code: str, used_names: set[str]) -> str:
    base_name = slugify(indicator_name)
    candidate = slugify(base_name, max_length=VARIABLE_NAME_MAX_LENGTH)
    if candidate not in used_names:
        return candidate

    suffix = slugify(indicator_code, max_length=24)
    if not suffix:
        suffix = "code"

    trimmed_base = base_name[: max(1, VARIABLE_NAME_MAX_LENGTH - len(suffix) - 1)].strip("_")
    candidate = f"{trimmed_base}_{suffix}".strip("_")

    counter = 2
    while candidate in used_names:
        counter_suffix = f"_{counter}"
        max_base_length = max(1, VARIABLE_NAME_MAX_LENGTH - len(suffix) - len(counter_suffix) - 1)
        trimmed_base = base_name[:max_base_length].strip("_")
        candidate = f"{trimmed_base}_{suffix}{counter_suffix}".strip("_")
        counter += 1

    return candidate


def assign_variable_names(shortlist: pd.DataFrame) -> pd.DataFrame:
    named = shortlist.copy()
    used_names: set[str] = set()
    variable_names: list[str] = []

    for _, row in named.iterrows():
        indicator_code = str(row["indicator_code"])
        indicator_name = str(row["indicator_name"])
        variable_name = (
            "life_expectancy_at_birth"
            if indicator_code == TARGET_INDICATOR
            else make_unique_variable_name(indicator_name, indicator_code, used_names)
        )
        used_names.add(variable_name)
        variable_names.append(variable_name)

    named["variable_name"] = variable_names
    return named


def choose_single_dimension(frame: pd.DataFrame) -> pd.DataFrame:
    """Try to keep a single comparable dimension per indicator.

    Many WHO indicators include sex, age or other dimensions in Dim1. The first
    dataset should be broad and comparable, so this helper prefers both-sexes or
    total values when available. If no preferred value exists, it keeps all rows.
    """
    if "Dim1" not in frame.columns or frame["Dim1"].dropna().empty:
        return frame

    dim1_as_text = frame["Dim1"].astype(str)
    preferred_mask = dim1_as_text.isin(PREFERRED_DIM1_VALUES)
    if preferred_mask.any():
        return frame.loc[preferred_mask].copy()

    distinct_values = sorted({value for value in dim1_as_text.loc[frame["Dim1"].notna()].tolist() if value})
    if len(distinct_values) <= 1:
        return frame

    raise ValueError(
        "indicator has multiple Dim1 values and no preferred aggregate: "
        + ", ".join(distinct_values[:5])
    )


def ensure_single_dimension_values(frame: pd.DataFrame) -> pd.DataFrame:
    for column in DIMENSION_VALUE_COLUMNS[1:]:
        if column not in frame.columns:
            continue
        values = sorted({str(value) for value in frame[column].dropna().tolist() if str(value).strip()})
        if len(values) > 1:
            raise ValueError(f"indicator has multiple {column} values and cannot be collapsed safely")
    return frame


def normalize_one_indicator(client: WHOGHOClient, indicator_code: str, variable_name: str) -> pd.DataFrame:
    raw = client.indicator_data(indicator_code)
    frame = normalize_indicator_frame(raw)

    required = {"SpatialDim", "TimeDim", "NumericValue"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Indicator {indicator_code} is missing required columns: {sorted(missing)}")

    if "SpatialDimType" in frame.columns:
        country_like = frame["SpatialDimType"].astype(str).str.upper().isin(COUNTRY_SPATIAL_TYPES)
        if country_like.any():
            frame = frame.loc[country_like].copy()

    frame = choose_single_dimension(frame)
    frame = ensure_single_dimension_values(frame)
    frame = frame.dropna(subset=["SpatialDim", "TimeDim", "NumericValue"]).copy()
    frame["TimeDim"] = pd.to_numeric(frame["TimeDim"], errors="coerce").astype("Int64")
    frame["NumericValue"] = pd.to_numeric(frame["NumericValue"], errors="coerce")
    frame = frame.dropna(subset=["TimeDim", "NumericValue"])

    group_columns = ["SpatialDim", "TimeDim"]
    if "ParentLocationCode" in frame.columns:
        group_columns.append("ParentLocationCode")
    if "ParentLocation" in frame.columns:
        group_columns.append("ParentLocation")

    collapsed = (
        frame.groupby(group_columns, dropna=False)["NumericValue"]
        .mean()
        .reset_index()
        .rename(
            columns={
                "SpatialDim": "country_code",
                "TimeDim": "year",
                "ParentLocationCode": "region_code",
                "ParentLocation": "region",
                "NumericValue": variable_name,
            }
        )
    )
    collapsed["year"] = collapsed["year"].astype(int)
    return collapsed


def add_data_quality_features(dataset: pd.DataFrame, indicator_columns: list[str]) -> pd.DataFrame:
    dataset = dataset.copy()
    feature_columns = [col for col in indicator_columns if col != "life_expectancy_at_birth"]
    if not feature_columns:
        dataset["available_indicator_count"] = 0
        dataset["missing_indicator_count"] = 0
        dataset["data_completeness_score"] = pd.NA
        return dataset

    dataset["available_indicator_count"] = dataset[feature_columns].notna().sum(axis=1)
    dataset["missing_indicator_count"] = dataset[feature_columns].isna().sum(axis=1)
    dataset["data_completeness_score"] = dataset["available_indicator_count"] / len(feature_columns)
    return dataset


def main() -> None:
    if not SHORTLIST_PATH.exists():
        raise SystemExit("Run scripts/04_profile_indicator_coverage.py first.")

    shortlist = pd.read_csv(SHORTLIST_PATH)
    if shortlist.empty:
        raise SystemExit("Shortlist is empty. Inspect coverage profile thresholds.")

    # Ensure target is present even if coverage shortlist did not include it.
    target_row = pd.DataFrame(
        [
            {
                "theme": "outcome_life_expectancy",
                "indicator_code": TARGET_INDICATOR,
                "indicator_name": "Life expectancy at birth (years)",
            }
        ]
    )
    shortlist = pd.concat([target_row, shortlist], ignore_index=True)
    shortlist = shortlist.drop_duplicates(subset=["indicator_code"], keep="first").reset_index(drop=True)
    shortlist = assign_variable_names(shortlist)

    client = WHOGHOClient()
    frames: list[pd.DataFrame] = []
    dictionary_rows: list[dict[str, str]] = []

    print(f"Building dataset from {len(shortlist):,} indicators...")

    for index, row in shortlist.iterrows():
        code = str(row["indicator_code"])
        name = str(row["indicator_name"])
        theme = str(row.get("theme", "unknown"))
        variable_name = str(row["variable_name"])

        print(f"[{index + 1:02d}/{len(shortlist):02d}] {code} -> {variable_name}")
        try:
            indicator_frame = normalize_one_indicator(client, code, variable_name)
        except Exception as exc:  # noqa: BLE001 - keep pipeline moving during exploration
            print(f"    skipped: {exc}")
            continue

        if indicator_frame.empty:
            print("    skipped: empty after normalization")
            continue

        frames.append(indicator_frame)
        dictionary_rows.append(
            {
                "variable_name": variable_name,
                "indicator_code": code,
                "indicator_name": name,
                "theme": theme,
            }
        )

    if not frames:
        raise SystemExit("No indicator frames could be built.")

    id_columns = ["country_code", "year", "region_code", "region"]
    dataset = frames[0]
    for frame in frames[1:]:
        merge_columns = [col for col in id_columns if col in dataset.columns and col in frame.columns]
        dataset = dataset.merge(frame, how="outer", on=merge_columns)

    indicator_columns = [row["variable_name"] for row in dictionary_rows if row["variable_name"] in dataset.columns]
    dataset = add_data_quality_features(dataset, indicator_columns)

    sort_columns = [col for col in ["region", "country_code", "year"] if col in dataset.columns]
    dataset = dataset.sort_values(sort_columns).reset_index(drop=True)

    dictionary = pd.DataFrame(dictionary_rows).drop_duplicates(subset=["variable_name"])

    dataset.to_csv(DATASET_CSV_PATH, index=False)
    dataset.to_parquet(DATASET_PARQUET_PATH, index=False)
    dictionary.to_csv(DICTIONARY_PATH, index=False)

    print("\nDataset exported:")
    print(f"- {DATASET_CSV_PATH.relative_to(PROJECT_ROOT)} | rows={len(dataset):,} | cols={len(dataset.columns):,}")
    print(f"- {DATASET_PARQUET_PATH.relative_to(PROJECT_ROOT)}")
    print(f"- {DICTIONARY_PATH.relative_to(PROJECT_ROOT)}")
    print("\nDataset preview:")
    print(dataset.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
