"""Analyze champion-model residuals for country-year life expectancy predictions.

Run from the repository root:

    python scripts/10_analyze_model_residuals.py

Inputs:
    outputs/tables/model_comparison_metrics.csv
    outputs/tables/all_model_predictions.csv
    data/processed/who_country_year_modeling_ready.csv

Outputs:
    outputs/tables/model_error_by_model.csv
    outputs/tables/model_error_by_model_region.csv
    outputs/tables/model_error_by_model_year.csv
    outputs/tables/residuals_by_country.csv
    outputs/tables/residuals_by_region.csv
    outputs/tables/residuals_by_year.csv
    outputs/tables/top_positive_residuals.csv
    outputs/tables/top_negative_residuals.csv
    outputs/tables/executive_findings.csv
    outputs/figures/11_residuals_by_region.png
    outputs/figures/12_residuals_by_year.png
    outputs/figures/13_top_country_residuals.png
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
METRICS_PATH = PROJECT_ROOT / 'outputs' / 'tables' / 'model_comparison_metrics.csv'
PREDICTIONS_PATH = PROJECT_ROOT / 'outputs' / 'tables' / 'all_model_predictions.csv'
MODELING_DATA_PATH = PROJECT_ROOT / 'data' / 'processed' / 'who_country_year_modeling_ready.csv'
TABLES_DIR = PROJECT_ROOT / 'outputs' / 'tables'
FIGURES_DIR = PROJECT_ROOT / 'outputs' / 'figures'

TABLES_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

TOP_N = 15
RESIDUAL_FIGURE_NAMES = {
    'region': '11_residuals_by_region.png',
    'year': '12_residuals_by_year.png',
    'country': '13_top_country_residuals.png',
}
LEGACY_RESIDUAL_FIGURES = [
    '11_residuals_by_region_tabpfn.png',
    '12_residuals_by_year_tabpfn.png',
    '13_top_country_residuals_tabpfn.png',
]


def savefig(name: str) -> None:
    path = FIGURES_DIR / name
    plt.tight_layout()
    plt.savefig(path, dpi=180, bbox_inches='tight')
    plt.close()
    print(f'Saved: {path.relative_to(PROJECT_ROOT)}')


def remove_legacy_figures() -> None:
    for name in LEGACY_RESIDUAL_FIGURES:
        path = FIGURES_DIR / name
        if path.exists():
            path.unlink()
            print(f'Removed legacy figure: {path.relative_to(PROJECT_ROOT)}')



def load_predictions() -> pd.DataFrame:
    if not PREDICTIONS_PATH.exists():
        raise SystemExit('Run scripts/08_train_baseline_models.py first.')
    predictions = pd.read_csv(PREDICTIONS_PATH)
    expected = {'country_code', 'year', 'region', 'model', 'actual', 'predicted', 'residual', 'abs_error'}
    missing = expected.difference(predictions.columns)
    if missing:
        raise SystemExit(f'Prediction file is missing columns: {sorted(missing)}')
    return predictions



def load_champion_model(predictions: pd.DataFrame) -> str:
    if METRICS_PATH.exists():
        metrics = pd.read_csv(METRICS_PATH)
        if not metrics.empty:
            return str(metrics.sort_values('test_mae', ascending=True).iloc[0]['model'])
    summary = predictions.groupby('model', dropna=False).agg(mean_abs_error=('abs_error', 'mean')).reset_index()
    return str(summary.sort_values('mean_abs_error', ascending=True).iloc[0]['model'])



def enrich_predictions(predictions: pd.DataFrame) -> pd.DataFrame:
    if not MODELING_DATA_PATH.exists():
        return predictions

    modeling = pd.read_csv(MODELING_DATA_PATH)
    enrich_cols = [
        'country_code',
        'year',
        'available_indicator_count',
        'missing_indicator_count',
        'data_completeness_score',
    ]
    enrich_cols = [col for col in enrich_cols if col in modeling.columns]
    if len(enrich_cols) <= 2:
        return predictions
    return predictions.merge(modeling[enrich_cols], on=['country_code', 'year'], how='left')



def summarize_model_errors(predictions: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    by_model = (
        predictions.groupby('model', dropna=False)
        .agg(rows=('country_code', 'size'), mean_abs_error=('abs_error', 'mean'), mean_residual=('residual', 'mean'))
        .reset_index()
        .sort_values('mean_abs_error', ascending=True)
    )
    by_model_region = (
        predictions.groupby(['model', 'region'], dropna=False)
        .agg(rows=('country_code', 'size'), mean_abs_error=('abs_error', 'mean'), mean_residual=('residual', 'mean'))
        .reset_index()
        .sort_values(['model', 'mean_abs_error'], ascending=[True, True])
    )
    by_model_year = (
        predictions.groupby(['model', 'year'], dropna=False)
        .agg(rows=('country_code', 'size'), mean_abs_error=('abs_error', 'mean'), mean_residual=('residual', 'mean'))
        .reset_index()
        .sort_values(['model', 'year'])
    )
    return by_model, by_model_region, by_model_year



def summarize_by_country(predictions: pd.DataFrame) -> pd.DataFrame:
    aggregations: dict[str, tuple[str, str]] = {
        'test_years': ('year', 'nunique'),
        'min_year': ('year', 'min'),
        'max_year': ('year', 'max'),
        'mean_actual': ('actual', 'mean'),
        'mean_predicted': ('predicted', 'mean'),
        'mean_residual': ('residual', 'mean'),
        'mean_abs_error': ('abs_error', 'mean'),
        'max_abs_error': ('abs_error', 'max'),
    }
    if 'data_completeness_score' in predictions.columns:
        aggregations['mean_data_completeness'] = ('data_completeness_score', 'mean')

    return (
        predictions.groupby(['country_code', 'region'], dropna=False)
        .agg(**aggregations)
        .reset_index()
        .sort_values('mean_abs_error', ascending=False)
    )



def summarize_by_region(predictions: pd.DataFrame) -> pd.DataFrame:
    aggregations: dict[str, tuple[str, str]] = {
        'rows': ('country_code', 'size'),
        'countries': ('country_code', 'nunique'),
        'mean_actual': ('actual', 'mean'),
        'mean_predicted': ('predicted', 'mean'),
        'mean_residual': ('residual', 'mean'),
        'mean_abs_error': ('abs_error', 'mean'),
        'median_abs_error': ('abs_error', 'median'),
        'max_abs_error': ('abs_error', 'max'),
    }
    if 'data_completeness_score' in predictions.columns:
        aggregations['mean_data_completeness'] = ('data_completeness_score', 'mean')

    return (
        predictions.groupby('region', dropna=False)
        .agg(**aggregations)
        .reset_index()
        .sort_values('mean_abs_error', ascending=False)
    )



def summarize_by_year(predictions: pd.DataFrame) -> pd.DataFrame:
    return (
        predictions.groupby('year', dropna=False)
        .agg(
            rows=('country_code', 'size'),
            countries=('country_code', 'nunique'),
            mean_actual=('actual', 'mean'),
            mean_predicted=('predicted', 'mean'),
            mean_residual=('residual', 'mean'),
            mean_abs_error=('abs_error', 'mean'),
            median_abs_error=('abs_error', 'median'),
            max_abs_error=('abs_error', 'max'),
        )
        .reset_index()
        .sort_values('year')
    )



def build_outlier_tables(predictions: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    positive = predictions.sort_values('residual', ascending=False).head(TOP_N).copy()
    negative = predictions.sort_values('residual', ascending=True).head(TOP_N).copy()
    return positive, negative



def plot_region_residuals(region_summary: pd.DataFrame, champion_name: str) -> None:
    plot_data = region_summary.sort_values('mean_abs_error', ascending=True)
    plt.figure(figsize=(10, 5.5))
    plt.barh(plot_data['region'].fillna('Unknown'), plot_data['mean_abs_error'])
    plt.xlabel('Mean absolute error')
    plt.ylabel('WHO region')
    plt.title(f'{champion_name}: prediction error by WHO region')
    savefig(RESIDUAL_FIGURE_NAMES['region'])



def plot_year_residuals(year_summary: pd.DataFrame, champion_name: str) -> None:
    plt.figure(figsize=(11, 5))
    plt.plot(year_summary['year'], year_summary['mean_abs_error'], marker='o', linewidth=1.6)
    plt.xlabel('Year')
    plt.ylabel('Mean absolute error')
    plt.title(f'{champion_name}: prediction error over time')
    savefig(RESIDUAL_FIGURE_NAMES['year'])



def plot_country_residuals(country_summary: pd.DataFrame, champion_name: str) -> None:
    top = country_summary.sort_values('mean_abs_error', ascending=False).head(TOP_N).copy()
    top['label'] = top['country_code'] + ' · ' + top['region'].fillna('Unknown')
    top = top.sort_values('mean_abs_error', ascending=True)

    plt.figure(figsize=(10, 6.8))
    plt.barh(top['label'], top['mean_abs_error'])
    plt.xlabel('Mean absolute error')
    plt.ylabel('Country / region')
    plt.title(f'Countries with highest average prediction error for {champion_name}')
    savefig(RESIDUAL_FIGURE_NAMES['country'])



def build_executive_findings(
    predictions: pd.DataFrame,
    country_summary: pd.DataFrame,
    region_summary: pd.DataFrame,
    year_summary: pd.DataFrame,
    positive: pd.DataFrame,
    negative: pd.DataFrame,
    champion_name: str,
) -> pd.DataFrame:
    best_region = region_summary.sort_values('mean_abs_error', ascending=True).iloc[0]
    worst_region = region_summary.sort_values('mean_abs_error', ascending=False).iloc[0]
    best_year = year_summary.sort_values('mean_abs_error', ascending=True).iloc[0]
    worst_year = year_summary.sort_values('mean_abs_error', ascending=False).iloc[0]
    highest_positive = positive.iloc[0]
    highest_negative = negative.iloc[0]
    highest_country_error = country_summary.iloc[0]

    rows = [
        {
            'finding_id': 'champion_model',
            'finding': 'Best-performing model on the temporal test split.',
            'metric': champion_name,
            'value': predictions['abs_error'].mean(),
            'context': 'Champion selected from the current global benchmark.',
        },
        {
            'finding_id': 'overall_error',
            'finding': 'Champion model predicted recent country-year life expectancy with low average error.',
            'metric': 'mean_absolute_error',
            'value': predictions['abs_error'].mean(),
            'context': 'Average absolute prediction error across all champion-model test rows.',
        },
        {
            'finding_id': 'best_region',
            'finding': 'Lowest regional prediction error.',
            'metric': str(best_region['region']),
            'value': best_region['mean_abs_error'],
            'context': 'Region where the champion model was most accurate on average.',
        },
        {
            'finding_id': 'worst_region',
            'finding': 'Highest regional prediction error.',
            'metric': str(worst_region['region']),
            'value': worst_region['mean_abs_error'],
            'context': 'Region where the champion model had the largest average error.',
        },
        {
            'finding_id': 'best_year',
            'finding': 'Lowest yearly prediction error.',
            'metric': int(best_year['year']),
            'value': best_year['mean_abs_error'],
            'context': 'Test year with the lowest average absolute error.',
        },
        {
            'finding_id': 'worst_year',
            'finding': 'Highest yearly prediction error.',
            'metric': int(worst_year['year']),
            'value': worst_year['mean_abs_error'],
            'context': 'Test year with the highest average absolute error.',
        },
        {
            'finding_id': 'positive_outlier',
            'finding': 'Observed life expectancy was higher than expected.',
            'metric': f"{highest_positive['country_code']} {int(highest_positive['year'])}",
            'value': highest_positive['residual'],
            'context': 'Largest positive residual: actual minus predicted.',
        },
        {
            'finding_id': 'negative_outlier',
            'finding': 'Observed life expectancy was lower than expected.',
            'metric': f"{highest_negative['country_code']} {int(highest_negative['year'])}",
            'value': highest_negative['residual'],
            'context': 'Largest negative residual: actual minus predicted.',
        },
        {
            'finding_id': 'country_error_focus',
            'finding': 'Country with highest average prediction error across test years.',
            'metric': str(highest_country_error['country_code']),
            'value': highest_country_error['mean_abs_error'],
            'context': 'Useful candidate for qualitative follow-up in the final report.',
        },
    ]
    return pd.DataFrame(rows)



def main() -> None:
    all_predictions = enrich_predictions(load_predictions())
    champion_name = load_champion_model(all_predictions)
    predictions = all_predictions[all_predictions['model'] == champion_name].copy()
    if predictions.empty:
        raise SystemExit(
            f'Champion model "{champion_name}" was selected from model_comparison_metrics.csv '
            'but is missing from outputs/tables/all_model_predictions.csv. '
            'Rerun scripts/09_train_tabpfn_priorlabs.py if the external benchmark was updated.'
        )
    remove_legacy_figures()

    model_summary, model_region_summary, model_year_summary = summarize_model_errors(all_predictions)
    country_summary = summarize_by_country(predictions)
    region_summary = summarize_by_region(predictions)
    year_summary = summarize_by_year(predictions)
    positive, negative = build_outlier_tables(predictions)
    findings = build_executive_findings(predictions, country_summary, region_summary, year_summary, positive, negative, champion_name)

    model_summary.to_csv(TABLES_DIR / 'model_error_by_model.csv', index=False)
    model_region_summary.to_csv(TABLES_DIR / 'model_error_by_model_region.csv', index=False)
    model_year_summary.to_csv(TABLES_DIR / 'model_error_by_model_year.csv', index=False)
    country_summary.to_csv(TABLES_DIR / 'residuals_by_country.csv', index=False)
    region_summary.to_csv(TABLES_DIR / 'residuals_by_region.csv', index=False)
    year_summary.to_csv(TABLES_DIR / 'residuals_by_year.csv', index=False)
    positive.to_csv(TABLES_DIR / 'top_positive_residuals.csv', index=False)
    negative.to_csv(TABLES_DIR / 'top_negative_residuals.csv', index=False)
    findings.to_csv(TABLES_DIR / 'executive_findings.csv', index=False)

    plot_region_residuals(region_summary, champion_name)
    plot_year_residuals(year_summary, champion_name)
    plot_country_residuals(country_summary, champion_name)

    print(f'Residual analysis completed for champion model: {champion_name}')
    print('\nExecutive findings:')
    print(findings.to_string(index=False))


if __name__ == '__main__':
    main()
