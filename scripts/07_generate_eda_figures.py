"""Generate the first static EDA figures for the WHO project.

Run from the repository root:

    python scripts/07_generate_eda_figures.py

Inputs:
    data/processed/who_country_year_dataset.csv
    data/processed/who_country_year_modeling_ready.csv
    outputs/tables/variable_missingness.csv
    outputs/tables/year_coverage.csv

Outputs:
    outputs/figures/*.png
    outputs/tables/eda_key_findings.csv

These charts are designed as the first visual layer for the final report.
They use the full dataset for data-quality analysis and the modeling-ready
subset for outcome relationships.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = PROJECT_ROOT / "data" / "processed" / "who_country_year_dataset.csv"
MODELING_PATH = PROJECT_ROOT / "data" / "processed" / "who_country_year_modeling_ready.csv"
MISSINGNESS_PATH = PROJECT_ROOT / "outputs" / "tables" / "variable_missingness.csv"
YEAR_COVERAGE_PATH = PROJECT_ROOT / "outputs" / "tables" / "year_coverage.csv"
FIGURES_DIR = PROJECT_ROOT / "outputs" / "figures"
TABLES_DIR = PROJECT_ROOT / "outputs" / "tables"

FIGURES_DIR.mkdir(parents=True, exist_ok=True)
TABLES_DIR.mkdir(parents=True, exist_ok=True)

TARGET = "life_expectancy_at_birth"


def savefig(name: str) -> None:
    path = FIGURES_DIR / name
    plt.tight_layout()
    plt.savefig(path, dpi=180, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path.relative_to(PROJECT_ROOT)}")


def find_column(columns: list[str], required_terms: list[str], forbidden_terms: list[str] | None = None) -> str | None:
    forbidden_terms = forbidden_terms or []
    for column in columns:
        normalized = column.lower()
        if all(term in normalized for term in required_terms) and not any(term in normalized for term in forbidden_terms):
            return column
    return None


def plot_variable_missingness(missingness: pd.DataFrame) -> None:
    top = missingness.sort_values("non_null_share", ascending=False).head(15).copy()
    top["label"] = top["variable_name"].str.wrap(36)

    plt.figure(figsize=(11, 7))
    plt.barh(top["label"], top["non_null_share"])
    plt.gca().invert_yaxis()
    plt.xlabel("Non-null share")
    plt.ylabel("Variable")
    plt.title("WHO indicators with the highest coverage in the analytical dataset")
    plt.xlim(0, 1)
    savefig("01_variable_coverage_top15.png")


def plot_year_coverage(year_coverage: pd.DataFrame) -> None:
    recent = year_coverage.loc[year_coverage["year"] >= 1990].copy()
    plt.figure(figsize=(12, 5))
    plt.plot(recent["year"], recent["mean_completeness"], marker="o", linewidth=1.5, markersize=3)
    plt.xlabel("Year")
    plt.ylabel("Mean data completeness score")
    plt.title("Average WHO indicator completeness by year, 1990 onward")
    plt.ylim(0, max(0.05, recent["mean_completeness"].max() * 1.15))
    savefig("02_yearly_data_completeness.png")


def plot_region_completeness(dataset: pd.DataFrame) -> None:
    region = (
        dataset.loc[dataset["year"] >= 2000]
        .groupby("region", dropna=False)
        .agg(
            mean_completeness=("data_completeness_score", "mean"),
            rows=("country_code", "size"),
            countries=("country_code", "nunique"),
        )
        .reset_index()
        .sort_values("mean_completeness", ascending=True)
    )
    plt.figure(figsize=(10, 5.8))
    plt.barh(region["region"].fillna("Unknown"), region["mean_completeness"])
    plt.xlabel("Mean completeness score")
    plt.ylabel("WHO region")
    plt.title("Data completeness differs by WHO region, 2000 onward")
    plt.xlim(0, max(0.05, region["mean_completeness"].max() * 1.2))
    savefig("03_completeness_by_region.png")


def plot_life_expectancy_trend(modeling: pd.DataFrame) -> None:
    if TARGET not in modeling.columns:
        return
    trend = (
        modeling.groupby(["year", "region"], dropna=False)[TARGET]
        .mean()
        .reset_index()
        .sort_values("year")
    )
    plt.figure(figsize=(12, 6))
    for region, frame in trend.groupby("region", dropna=False):
        plt.plot(frame["year"], frame[TARGET], linewidth=1.6, label=str(region))
    plt.xlabel("Year")
    plt.ylabel("Life expectancy at birth")
    plt.title("Life expectancy trend by WHO region in the modeling-ready dataset")
    plt.legend(loc="best", fontsize=8)
    savefig("04_life_expectancy_trend_by_region.png")


def plot_scatter_relationships(modeling: pd.DataFrame) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    columns = modeling.columns.tolist()

    candidates = [
        ("under5_mortality", find_column(columns, ["under", "mortality"])),
        ("infant_mortality", find_column(columns, ["infant", "mortality"])),
        ("neonatal_mortality", find_column(columns, ["neonatal", "mortality"])),
        ("maternal_mortality", find_column(columns, ["maternal", "mortality"])),
        ("immunization", find_column(columns, ["immunization"])),
        ("health_expenditure", find_column(columns, ["health", "expenditure"])),
        ("tuberculosis", find_column(columns, ["tuberculosis"])),
    ]

    for label, column in candidates:
        if column is None or TARGET not in modeling.columns:
            continue
        frame = modeling[[column, TARGET, "region"]].dropna().copy()
        if len(frame) < 50:
            continue
        corr = frame[column].corr(frame[TARGET])
        findings.append(
            {
                "chart": f"scatter_{label}",
                "variable": column,
                "rows": len(frame),
                "pearson_corr_with_life_expectancy": corr,
            }
        )

        plt.figure(figsize=(8, 6))
        for region, group in frame.groupby("region", dropna=False):
            plt.scatter(group[column], group[TARGET], s=16, alpha=0.55, label=str(region))
        plt.xlabel(column.replace("_", " "))
        plt.ylabel("Life expectancy at birth")
        plt.title(f"{column.replace('_', ' ').title()} vs life expectancy")
        if frame["region"].nunique(dropna=True) <= 8:
            plt.legend(loc="best", fontsize=7)
        savefig(f"05_scatter_{label}_vs_life_expectancy.png")

    return findings


def export_key_findings(dataset: pd.DataFrame, modeling: pd.DataFrame, missingness: pd.DataFrame, scatter_findings: list[dict[str, object]]) -> None:
    rows: list[dict[str, object]] = []
    rows.append({"finding_type": "dataset", "metric": "full_rows", "value": len(dataset)})
    rows.append({"finding_type": "dataset", "metric": "modeling_ready_rows", "value": len(modeling)})
    rows.append({"finding_type": "dataset", "metric": "countries", "value": dataset["country_code"].nunique(dropna=True)})
    rows.append({"finding_type": "dataset", "metric": "min_year", "value": dataset["year"].min()})
    rows.append({"finding_type": "dataset", "metric": "max_year", "value": dataset["year"].max()})

    for _, row in missingness.head(8).iterrows():
        rows.append(
            {
                "finding_type": "variable_coverage",
                "metric": row["variable_name"],
                "value": row["non_null_share"],
            }
        )

    for item in scatter_findings:
        rows.append(
            {
                "finding_type": "correlation",
                "metric": item["variable"],
                "value": item["pearson_corr_with_life_expectancy"],
            }
        )

    findings = pd.DataFrame(rows)
    path = TABLES_DIR / "eda_key_findings.csv"
    findings.to_csv(path, index=False)
    print(f"Saved: {path.relative_to(PROJECT_ROOT)}")


def main() -> None:
    if not DATASET_PATH.exists() or not MODELING_PATH.exists():
        raise SystemExit("Run scripts/05_build_country_year_dataset.py and scripts/06_audit_dataset_quality.py first.")

    dataset = pd.read_csv(DATASET_PATH)
    modeling = pd.read_csv(MODELING_PATH)
    missingness = pd.read_csv(MISSINGNESS_PATH)
    year_coverage = pd.read_csv(YEAR_COVERAGE_PATH)

    plot_variable_missingness(missingness)
    plot_year_coverage(year_coverage)
    plot_region_completeness(dataset)
    plot_life_expectancy_trend(modeling)
    scatter_findings = plot_scatter_relationships(modeling)
    export_key_findings(dataset, modeling, missingness, scatter_findings)

    print("\nEDA figure generation completed.")


if __name__ == "__main__":
    main()
