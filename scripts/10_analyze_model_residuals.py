"""Analyze TabPFN residuals for country-year life expectancy predictions.

Run from the repository root:

    python scripts/10_analyze_model_residuals.py

Inputs:
    outputs/tables/tabpfn_priorlabs_predictions.csv
    data/processed/who_country_year_modeling_ready.csv

Outputs:
    outputs/tables/residuals_by_country.csv
    outputs/tables/residuals_by_region.csv
    outputs/tables/residuals_by_year.csv
    outputs/tables/top_positive_residuals.csv
    outputs/tables/top_negative_residuals.csv
    outputs/tables/executive_findings.csv
    outputs/figures/11_residuals_by_region_tabpfn.png
    outputs/figures/12_residuals_by_year_tabpfn.png
    outputs/figures/13_top_country_residuals_tabpfn.png

Interpretation:
    residual = actual - predicted
    positive residual -> observed life expectancy is higher than expected
    negative residual -> observed life expectancy is lower than expected
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PREDICTIONS_PATH = PROJECT_ROOT / "outputs" / "tables" / "tabpfn_priorlabs_predictions.csv"
MODELING_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "who_country_year_modeling_ready.csv"
TABLES_DIR = PROJECT_ROOT / "outputs" / "tables"
FIGURES_DIR = PROJECT_ROOT / "outputs" / "figures"

TABLES_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

TOP_N = 15


def savefig(name: str) -> None:
    path = FIGURES_DIR / name
    plt.tight_layout()
    plt.savefig(path, dpi=180, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path.relative_to(PROJECT_ROOT)}")


def load_predictions() -> pd.DataFrame:
    if not PREDICTIONS_PATH.exists():
        raise SystemExit("Run scripts/09_train_tabpfn_priorlabs.py first.")
    predictions = pd.read_csv(PREDICTIONS_PATH)
    expected = {"country_code", "year", "region", "actual", "predicted", "residual", "abs_error"}
    missing = expected.difference(predictions.columns)
    if missing:
        raise SystemExit(f"Prediction file is missing columns: {sorted(missing)}")
    return predictions


def enrich_predictions(predictions: pd.DataFrame) -> pd.DataFrame:
    if not MODELING_DATA_PATH.exists():
        return predictions

    modeling = pd.read_csv(MODELING_DATA_PATH)
    enrich_cols = [
        "country_code",
        "year",
        "available_indicator_count",
        "missing_indicator_count",
        "data_completeness_score",
    ]
    enrich_cols = [col for col in enrich_cols if col in modeling.columns]
    if len(enrich_cols) <= 2:
        return predictions

    return predictions.merge(modeling[enrich_cols], on=["country_code", "year"], how="left")


def summarize_by_country(predictions: pd.DataFrame) -> pd.DataFrame:
    return (
        predictions.groupby(["country_code", "region"], dropna=False)
        .agg(
            test_years=("year", "nunique"),
            min_year=("year", "min"),
            max_year=("year", "max"),
            mean_actual=("actual", "mean"),
            mean_predicted=("predicted", "mean"),
            mean_residual=("residual", "mean"),
            mean_abs_error=("abs_error", "mean"),
            max_abs_error=("abs_error", "max"),
            mean_data_completeness=("data_completeness_score", "mean") if "data_completeness_score" in predictions.columns else ("abs_error", "size"),
        )
        .reset_index()
        .sort_values("mean_abs_error", ascending=False)
    )


def summarize_by_region(predictions: pd.DataFrame) -> pd.DataFrame:
    return (
        predictions.groupby("region", dropna=False)
        .agg(
            rows=("country_code", "size"),
            countries=("country_code", "nunique"),
            mean_actual=("actual", "mean"),
            mean_predicted=("predicted", "mean"),
            mean_residual=("residual", "mean"),
            mean_abs_error=("abs_error", "mean"),
            median_abs_error=("abs_error", "median"),
            max_abs_error=("abs_error", "max"),
            mean_data_completeness=("data_completeness_score", "mean") if "data_completeness_score" in predictions.columns else ("abs_error", "size"),
        )
        .reset_index()
        .sort_values("mean_abs_error", ascending=False)
    )


def summarize_by_year(predictions: pd.DataFrame) -> pd.DataFrame:
    return (
        predictions.groupby("year", dropna=False)
        .agg(
            rows=("country_code", "size"),
            countries=("country_code", "nunique"),
            mean_actual=("actual", "mean"),
            mean_predicted=("predicted", "mean"),
            mean_residual=("residual", "mean"),
            mean_abs_error=("abs_error", "mean"),
            median_abs_error=("abs_error", "median"),
            max_abs_error=("abs_error", "max"),
        )
        .reset_index()
        .sort_values("year")
    )


def build_outlier_tables(predictions: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    positive = predictions.sort_values("residual", ascending=False).head(TOP_N).copy()
    negative = predictions.sort_values("residual", ascending=True).head(TOP_N).copy()
    return positive, negative


def plot_region_residuals(region_summary: pd.DataFrame) -> None:
    plot_data = region_summary.sort_values("mean_abs_error", ascending=True)
    plt.figure(figsize=(10, 5.5))
    plt.barh(plot_data["region"].fillna("Unknown"), plot_data["mean_abs_error"])
    plt.xlabel("Mean absolute error")
    plt.ylabel("WHO region")
    plt.title("TabPFN prediction error by WHO region")
    savefig("11_residuals_by_region_tabpfn.png")


def plot_year_residuals(year_summary: pd.DataFrame) -> None:
    plt.figure(figsize=(11, 5))
    plt.plot(year_summary["year"], year_summary["mean_abs_error"], marker="o", linewidth=1.6)
    plt.xlabel("Year")
    plt.ylabel("Mean absolute error")
    plt.title("TabPFN prediction error over time")
    savefig("12_residuals_by_year_tabpfn.png")


def plot_country_residuals(country_summary: pd.DataFrame) -> None:
    top = country_summary.sort_values("mean_abs_error", ascending=False).head(TOP_N).copy()
    top["label"] = top["country_code"] + " · " + top["region"].fillna("Unknown")
    top = top.sort_values("mean_abs_error", ascending=True)

    plt.figure(figsize=(10, 6.8))
    plt.barh(top["label"], top["mean_abs_error"])
    plt.xlabel("Mean absolute error")
    plt.ylabel("Country / region")
    plt.title("Countries with highest average TabPFN prediction error")
    savefig("13_top_country_residuals_tabpfn.png")


def build_executive_findings(
    predictions: pd.DataFrame,
    country_summary: pd.DataFrame,
    region_summary: pd.DataFrame,
    year_summary: pd.DataFrame,
    positive: pd.DataFrame,
    negative: pd.DataFrame,
) -> pd.DataFrame:
    best_region = region_summary.sort_values("mean_abs_error", ascending=True).iloc[0]
    worst_region = region_summary.sort_values("mean_abs_error", ascending=False).iloc[0]
    best_year = year_summary.sort_values("mean_abs_error", ascending=True).iloc[0]
    worst_year = year_summary.sort_values("mean_abs_error", ascending=False).iloc[0]
    highest_positive = positive.iloc[0]
    highest_negative = negative.iloc[0]
    highest_country_error = country_summary.iloc[0]

    rows = [
        {
            "finding_id": "overall_error",
            "finding": "TabPFN predicted recent country-year life expectancy with low average error.",
            "metric": "mean_absolute_error",
            "value": predictions["abs_error"].mean(),
            "context": "Average absolute prediction error across all test rows.",
        },
        {
            "finding_id": "best_region",
            "finding": "Lowest regional prediction error.",
            "metric": str(best_region["region"]),
            "value": best_region["mean_abs_error"],
            "context": "Region where the model was most accurate on average.",
        },
        {
            "finding_id": "worst_region",
            "finding": "Highest regional prediction error.",
            "metric": str(worst_region["region"]),
            "value": worst_region["mean_abs_error"],
            "context": "Region where the model had the largest average error.",
        },
        {
            "finding_id": "best_year",
            "finding": "Lowest yearly prediction error.",
            "metric": int(best_year["year"]),
            "value": best_year["mean_abs_error"],
            "context": "Test year with the lowest average absolute error.",
        },
        {
            "finding_id": "worst_year",
            "finding": "Highest yearly prediction error.",
            "metric": int(worst_year["year"]),
            "value": worst_year["mean_abs_error"],
            "context": "Test year with the highest average absolute error.",
        },
        {
            "finding_id": "positive_outlier",
            "finding": "Observed life expectancy was higher than expected.",
            "metric": f"{highest_positive['country_code']} {int(highest_positive['year'])}",
            "value": highest_positive["residual"],
            "context": "Largest positive residual: actual minus predicted.",
        },
        {
            "finding_id": "negative_outlier",
            "finding": "Observed life expectancy was lower than expected.",
            "metric": f"{highest_negative['country_code']} {int(highest_negative['year'])}",
            "value": highest_negative["residual"],
            "context": "Largest negative residual: actual minus predicted.",
        },
        {
            "finding_id": "country_error_focus",
            "finding": "Country with highest average prediction error across test years.",
            "metric": str(highest_country_error["country_code"]),
            "value": highest_country_error["mean_abs_error"],
            "context": "Useful candidate for qualitative follow-up in the final report.",
        },
    ]
    return pd.DataFrame(rows)


def main() -> None:
    predictions = enrich_predictions(load_predictions())

    country_summary = summarize_by_country(predictions)
    region_summary = summarize_by_region(predictions)
    year_summary = summarize_by_year(predictions)
    positive, negative = build_outlier_tables(predictions)
    findings = build_executive_findings(predictions, country_summary, region_summary, year_summary, positive, negative)

    country_summary.to_csv(TABLES_DIR / "residuals_by_country.csv", index=False)
    region_summary.to_csv(TABLES_DIR / "residuals_by_region.csv", index=False)
    year_summary.to_csv(TABLES_DIR / "residuals_by_year.csv", index=False)
    positive.to_csv(TABLES_DIR / "top_positive_residuals.csv", index=False)
    negative.to_csv(TABLES_DIR / "top_negative_residuals.csv", index=False)
    findings.to_csv(TABLES_DIR / "executive_findings.csv", index=False)

    plot_region_residuals(region_summary)
    plot_year_residuals(year_summary)
    plot_country_residuals(country_summary)

    print("Residual analysis completed.")
    print("\nExecutive findings:")
    print(findings.to_string(index=False))
    print("\nFiles exported:")
    print("- outputs/tables/residuals_by_country.csv")
    print("- outputs/tables/residuals_by_region.csv")
    print("- outputs/tables/residuals_by_year.csv")
    print("- outputs/tables/top_positive_residuals.csv")
    print("- outputs/tables/top_negative_residuals.csv")
    print("- outputs/tables/executive_findings.csv")
    print("- outputs/figures/11_residuals_by_region_tabpfn.png")
    print("- outputs/figures/12_residuals_by_year_tabpfn.png")
    print("- outputs/figures/13_top_country_residuals_tabpfn.png")


if __name__ == "__main__":
    main()
