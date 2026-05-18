"""Train a heavy local benchmark for life expectancy prediction.

Run:
    python scripts/08_train_baseline_models.py

Outputs:
    outputs/tables/local_model_metrics.csv
    outputs/tables/local_model_predictions.csv
    outputs/tables/local_model_search_results.csv
    outputs/tables/local_model_feature_importance.csv
    outputs/tables/local_model_availability.csv
    outputs/tables/local_model_surface_payload.json
    outputs/tables/model_comparison_metrics.csv
    outputs/tables/all_model_predictions.csv
    outputs/figures/06_champion_actual_vs_predicted.png
    outputs/figures/07_champion_residuals_by_region.png
    outputs/figures/08_champion_feature_importance.png
    outputs/figures/14_local_model_comparison.png
    outputs/figures/15_local_model_error_by_year.png
    outputs/figures/16_response_surface_<model>.png
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import sys

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.models.benchmarking import (  # noqa: E402
    TARGET,
    build_local_model_specs,
    build_surface_frame,
    build_temporal_cv,
    choose_surface_features,
    evaluate_model,
    extract_feature_importance,
    feature_sets,
    fit_with_search,
    json_ready_search_results,
    merge_model_artifacts,
    surface_payload,
    temporal_train_test_split,
)

DATA_PATH = PROJECT_ROOT / 'data' / 'processed' / 'who_country_year_modeling_ready.csv'
FIGURES_DIR = PROJECT_ROOT / 'outputs' / 'figures'
TABLES_DIR = PROJECT_ROOT / 'outputs' / 'tables'
FIGURES_DIR.mkdir(parents=True, exist_ok=True)
TABLES_DIR.mkdir(parents=True, exist_ok=True)

SEARCH_ITERATIONS = int(os.getenv('LOCAL_BENCHMARK_SEARCH_ITER', '24'))
CV_SPLIT_COUNT = int(os.getenv('LOCAL_BENCHMARK_CV_SPLITS', '4'))
TOP_MODELS_FOR_YEAR_CHART = int(os.getenv('LOCAL_BENCHMARK_TOP_YEAR_MODELS', '4'))
TOP_MODELS_FOR_SURFACES = int(os.getenv('LOCAL_BENCHMARK_TOP_SURFACES', '2'))
CHAMPION_FIGURE_NAMES = {
    'actual_vs_predicted': '06_champion_actual_vs_predicted.png',
    'region_error': '07_champion_residuals_by_region.png',
    'importance': '08_champion_feature_importance.png',
}

LOCAL_METRICS_PATH = TABLES_DIR / 'local_model_metrics.csv'
LOCAL_PREDICTIONS_PATH = TABLES_DIR / 'local_model_predictions.csv'
LOCAL_SEARCH_PATH = TABLES_DIR / 'local_model_search_results.csv'
LOCAL_IMPORTANCE_PATH = TABLES_DIR / 'local_model_feature_importance.csv'
LOCAL_AVAILABILITY_PATH = TABLES_DIR / 'local_model_availability.csv'
LOCAL_SURFACE_PAYLOAD_PATH = TABLES_DIR / 'local_model_surface_payload.json'
COMPARISON_PATH = TABLES_DIR / 'model_comparison_metrics.csv'
ALL_PREDICTIONS_PATH = TABLES_DIR / 'all_model_predictions.csv'
TABPFN_METRICS_PATH = TABLES_DIR / 'tabpfn_priorlabs_metrics.csv'
TABPFN_PREDICTIONS_PATH = TABLES_DIR / 'tabpfn_priorlabs_predictions.csv'


def savefig(name: str) -> None:
    path = FIGURES_DIR / name
    plt.tight_layout()
    plt.savefig(path, dpi=180, bbox_inches='tight')
    plt.close()
    print(f'Saved: {path.relative_to(PROJECT_ROOT)}')



def plot_model_comparison(metrics: pd.DataFrame) -> None:
    ordered = metrics.sort_values('test_mae', ascending=True).copy()
    plt.figure(figsize=(10, 6.2))
    plt.barh(ordered['model'], ordered['test_mae'])
    plt.gca().invert_yaxis()
    plt.xlabel('Test MAE')
    plt.ylabel('Model')
    plt.title('Heavy local benchmark: model comparison on the temporal test split')
    savefig('14_local_model_comparison.png')



def plot_year_error(predictions: pd.DataFrame, metrics: pd.DataFrame) -> None:
    top_models = metrics.sort_values('test_mae', ascending=True)['model'].head(TOP_MODELS_FOR_YEAR_CHART).tolist()
    year_error = (
        predictions[predictions['model'].isin(top_models)]
        .groupby(['model', 'year'], dropna=False)
        .agg(mean_abs_error=('abs_error', 'mean'))
        .reset_index()
        .sort_values(['model', 'year'])
    )

    plt.figure(figsize=(11, 5.5))
    for model_name, frame in year_error.groupby('model', dropna=False):
        plt.plot(frame['year'], frame['mean_abs_error'], marker='o', linewidth=1.6, label=str(model_name))
    plt.xlabel('Year')
    plt.ylabel('Mean absolute error')
    plt.title('Temporal error profile for the strongest local models')
    plt.legend(loc='best', fontsize=8)
    savefig('15_local_model_error_by_year.png')



def plot_champion_outputs(champion_predictions: pd.DataFrame, importance: pd.DataFrame, champion_name: str) -> None:
    plt.figure(figsize=(7, 7))
    plt.scatter(champion_predictions['actual'], champion_predictions['predicted'], s=18, alpha=0.55)
    low = min(champion_predictions['actual'].min(), champion_predictions['predicted'].min())
    high = max(champion_predictions['actual'].max(), champion_predictions['predicted'].max())
    plt.plot([low, high], [low, high], linestyle='--', linewidth=1)
    plt.xlabel('Actual life expectancy')
    plt.ylabel('Predicted life expectancy')
    plt.title(f'{champion_name}: actual vs predicted')
    savefig(CHAMPION_FIGURE_NAMES['actual_vs_predicted'])

    residuals = (
        champion_predictions.groupby('region', dropna=False)
        .agg(mean_abs_error=('abs_error', 'mean'))
        .reset_index()
        .sort_values('mean_abs_error', ascending=True)
    )
    plt.figure(figsize=(10, 5.5))
    plt.barh(residuals['region'].fillna('Unknown'), residuals['mean_abs_error'])
    plt.xlabel('Mean absolute error')
    plt.ylabel('WHO region')
    plt.title(f'{champion_name}: prediction error by WHO region')
    savefig(CHAMPION_FIGURE_NAMES['region_error'])

    if importance.empty:
        return

    top = importance.head(15).copy()
    top['label'] = top['feature'].str.replace('_', ' ').str.wrap(36)
    plt.figure(figsize=(10, 7))
    plt.barh(top['label'], top['importance'])
    plt.gca().invert_yaxis()
    plt.xlabel(top['importance_type'].iloc[0].replace('_', ' ').title())
    plt.title(f'Top predictive signals for {champion_name}')
    savefig(CHAMPION_FIGURE_NAMES['importance'])



def plot_response_surface(payload: dict[str, object], *, rank: int) -> None:
    figure = plt.figure(figsize=(9.5, 7.4))
    axis = figure.add_subplot(111, projection='3d')

    x_values = payload['x']
    y_values = payload['y']
    z_values = payload['z']
    x_grid, y_grid = np.meshgrid(x_values, y_values)
    z_grid = np.array(z_values)

    masked_grid = np.ma.masked_invalid(z_grid)
    surface = axis.plot_surface(x_grid, y_grid, masked_grid, cmap='viridis', linewidth=0.35, edgecolor='black', alpha=0.93)
    axis.contourf(x_grid, y_grid, masked_grid, zdir='z', offset=float(masked_grid.min()), cmap='viridis', alpha=0.65)
    axis.set_xlabel(str(payload['feature_x']).replace('_', ' ').title(), labelpad=10)
    axis.set_ylabel(str(payload['feature_y']).replace('_', ' ').title(), labelpad=10)
    axis.set_zlabel('Predicted life expectancy', labelpad=10)
    axis.set_title(f"{payload['model']}: local response surface", pad=18)
    axis.view_init(elev=28, azim=-132)
    figure.colorbar(surface, shrink=0.62, aspect=14, pad=0.08)

    filename = f"{15 + rank:02d}_response_surface_{payload['model']}.png"
    savefig(filename)



def write_json(path: Path, payload: object) -> None:
    def sanitize(value: object) -> object:
        if isinstance(value, dict):
            return {key: sanitize(item) for key, item in value.items()}
        if isinstance(value, list):
            return [sanitize(item) for item in value]
        if isinstance(value, float) and (np.isnan(value) or np.isinf(value)):
            return None
        return value

    with path.open('w', encoding='utf-8') as file:
        json.dump(sanitize(payload), file, ensure_ascii=False, indent=2, allow_nan=False)
    print(f'Saved: {path.relative_to(PROJECT_ROOT)}')


def merge_optional_reference_artifacts(local_metrics: pd.DataFrame, local_predictions: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    tabpfn_metrics = pd.read_csv(TABPFN_METRICS_PATH) if TABPFN_METRICS_PATH.exists() else None
    tabpfn_predictions = pd.read_csv(TABPFN_PREDICTIONS_PATH) if TABPFN_PREDICTIONS_PATH.exists() else None
    return merge_model_artifacts(local_metrics, local_predictions, tabpfn_metrics, tabpfn_predictions)



def main() -> None:
    if not DATA_PATH.exists():
        raise SystemExit('Run scripts/06_audit_dataset_quality.py first.')

    data = pd.read_csv(DATA_PATH)
    train, test = temporal_train_test_split(data)
    numeric, categorical, features = feature_sets(data)
    cv_splits = build_temporal_cv(train, n_splits=CV_SPLIT_COUNT)
    specs, missing_optional = build_local_model_specs()

    availability_rows = [{'model': spec.name, 'status': 'available', 'dependency': spec.dependency or 'stdlib'} for spec in specs]
    availability_rows.extend(
        {'model': row['model'], 'status': 'missing_dependency', 'dependency': row['dependency'], 'reason': row['reason']}
        for row in missing_optional
    )

    metrics_rows: list[dict[str, object]] = []
    prediction_frames: list[pd.DataFrame] = []
    search_results = []
    importance_frames: list[pd.DataFrame] = []
    fitted_models: dict[str, object] = {}

    for spec in specs:
        print(f'Training {spec.name} with temporal tuning...')
        try:
            model, search_result = fit_with_search(spec, train, features, n_iter=SEARCH_ITERATIONS, cv_splits=cv_splits)
            metrics_row, prediction_frame = evaluate_model(spec.name, model, train, test, features)
            metrics_row['dependency'] = spec.dependency or 'local'
            metrics_row['best_cv_mae'] = search_result.best_cv_mae

            fitted_models[spec.name] = model
            search_results.append(search_result)
            metrics_rows.append(metrics_row)
            prediction_frames.append(prediction_frame)

            importance = extract_feature_importance(spec.name, model, numeric, categorical)
            if not importance.empty:
                importance_frames.append(importance)
        except Exception as exc:  # noqa: BLE001
            availability_rows.append(
                {
                    'model': spec.name,
                    'status': 'training_failed',
                    'dependency': spec.dependency or 'local',
                    'reason': str(exc),
                }
            )
            print(f'Skipping {spec.name}: {exc}')

    if not metrics_rows:
        raise SystemExit('No local models completed successfully.')

    metrics_df = pd.DataFrame(metrics_rows).sort_values('test_mae').reset_index(drop=True)
    predictions_df = pd.concat(prediction_frames, ignore_index=True)
    search_df = json_ready_search_results(search_results)
    importance_df = pd.concat(importance_frames, ignore_index=True) if importance_frames else pd.DataFrame(columns=['model', 'feature', 'importance', 'importance_type'])
    availability_df = pd.DataFrame(availability_rows)

    champion_name = str(metrics_df.iloc[0]['model'])
    champion_predictions = predictions_df[predictions_df['model'] == champion_name].copy()
    champion_importance = importance_df[importance_df['model'] == champion_name].copy()

    surface_payloads: list[dict[str, object]] = []
    for rank, model_name in enumerate(metrics_df['model'].head(TOP_MODELS_FOR_SURFACES).tolist(), start=1):
        importance = importance_df[importance_df['model'] == model_name].copy()
        feature_x, feature_y = choose_surface_features(train, importance if not importance.empty else None)
        surface_frame, meta = build_surface_frame(fitted_models[model_name], train, feature_x=feature_x, feature_y=feature_y)
        payload = surface_payload(model_name, surface_frame, meta)
        surface_payloads.append(payload)
        plot_response_surface(payload, rank=rank)

    metrics_df.to_csv(LOCAL_METRICS_PATH, index=False)
    predictions_df.to_csv(LOCAL_PREDICTIONS_PATH, index=False)
    search_df.to_csv(LOCAL_SEARCH_PATH, index=False)
    importance_df.to_csv(LOCAL_IMPORTANCE_PATH, index=False)
    availability_df.to_csv(LOCAL_AVAILABILITY_PATH, index=False)
    comparison_df, all_predictions_df = merge_optional_reference_artifacts(metrics_df, predictions_df)
    comparison_df.to_csv(COMPARISON_PATH, index=False)
    all_predictions_df.to_csv(ALL_PREDICTIONS_PATH, index=False)
    write_json(LOCAL_SURFACE_PAYLOAD_PATH, surface_payloads)

    plot_model_comparison(metrics_df)
    plot_year_error(predictions_df, metrics_df)
    plot_champion_outputs(champion_predictions, champion_importance, champion_name)

    print('\nHeavy local benchmark completed.')
    print(metrics_df[['model', 'test_mae', 'test_rmse', 'test_r2', 'best_cv_mae']].to_string(index=False))
    print(f'Champion local model: {champion_name}')


if __name__ == '__main__':
    main()



