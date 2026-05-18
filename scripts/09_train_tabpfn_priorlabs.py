"""Train and evaluate TabPFN via the Prior Labs REST API.

Run from the repository root:

    python scripts/09_train_tabpfn_priorlabs.py

Requirements:
    1. Create a local .env file from .env.example.
    2. Set PRIORLABS_API_KEY in .env for the optional TabPFN benchmark.
    3. Run scripts/08_train_baseline_models.py first for the local benchmark.

Outputs:
    data/interim/priorlabs/x_train.csv
    data/interim/priorlabs/y_train.csv
    data/interim/priorlabs/x_test.csv
    outputs/tables/tabpfn_priorlabs_metrics.csv
    outputs/tables/tabpfn_priorlabs_predictions.csv
    outputs/tables/model_comparison_metrics.csv
    outputs/tables/all_model_predictions.csv
    outputs/figures/09_tabpfn_actual_vs_predicted.png
    outputs/figures/10_model_comparison_mae.png
"""

from __future__ import annotations

import os
from pathlib import Path
import sys
from typing import Any

import httpx
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.data.who_client import resolve_requests_verify  # noqa: E402
from src.models.benchmarking import TARGET, feature_sets, merge_model_artifacts, preprocessor, temporal_train_test_split  # noqa: E402

DATA_PATH = PROJECT_ROOT / 'data' / 'processed' / 'who_country_year_modeling_ready.csv'
LOCAL_METRICS_PATH = PROJECT_ROOT / 'outputs' / 'tables' / 'local_model_metrics.csv'
LOCAL_PREDICTIONS_PATH = PROJECT_ROOT / 'outputs' / 'tables' / 'local_model_predictions.csv'
INTERIM_DIR = PROJECT_ROOT / 'data' / 'interim' / 'priorlabs'
TABLES_DIR = PROJECT_ROOT / 'outputs' / 'tables'
FIGURES_DIR = PROJECT_ROOT / 'outputs' / 'figures'
COMPARISON_PATH = TABLES_DIR / 'model_comparison_metrics.csv'
ALL_PREDICTIONS_PATH = TABLES_DIR / 'all_model_predictions.csv'

INTERIM_DIR.mkdir(parents=True, exist_ok=True)
TABLES_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

BASE_URL = 'https://api.priorlabs.ai'
REQUEST_TIMEOUT = 600


def savefig(name: str) -> None:
    path = FIGURES_DIR / name
    plt.tight_layout()
    plt.savefig(path, dpi=180, bbox_inches='tight')
    plt.close()
    print(f'Saved: {path.relative_to(PROJECT_ROOT)}')



def rmse(y_true: pd.Series, y_pred: np.ndarray) -> float:
    return float(np.sqrt(np.mean((y_true.to_numpy() - y_pred) ** 2)))



def load_api_key() -> str:
    load_dotenv(PROJECT_ROOT / '.env')
    return os.getenv('PRIORLABS_API_KEY', '').strip()



def prepare_tabpfn_matrices(data: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series, pd.DataFrame]:
    train, test = temporal_train_test_split(data)
    numeric, categorical, features = feature_sets(data)
    transformer = preprocessor(numeric, categorical, scale_numeric=True)

    x_train_array = transformer.fit_transform(train[features])
    x_test_array = transformer.transform(test[features])

    feature_names = list(numeric)
    if categorical:
        onehot = transformer.named_transformers_['cat'].named_steps['onehot']
        feature_names.extend(onehot.get_feature_names_out(categorical).tolist())

    x_train = pd.DataFrame(x_train_array, columns=feature_names)
    x_test = pd.DataFrame(x_test_array, columns=feature_names)
    y_train = train[TARGET].reset_index(drop=True)
    y_test = test[TARGET].reset_index(drop=True)

    metadata = test[['country_code', 'year', 'region', TARGET]].reset_index(drop=True).copy()
    return x_train, y_train, x_test, y_test, metadata



def write_upload_files(x_train: pd.DataFrame, y_train: pd.Series, x_test: pd.DataFrame) -> tuple[Path, Path, Path]:
    x_train_path = INTERIM_DIR / 'x_train.csv'
    y_train_path = INTERIM_DIR / 'y_train.csv'
    x_test_path = INTERIM_DIR / 'x_test.csv'

    x_train.to_csv(x_train_path, index=False)
    y_train.to_frame(name=TARGET).to_csv(y_train_path, index=False)
    x_test.to_csv(x_test_path, index=False)
    print(f'Saved upload files in {INTERIM_DIR.relative_to(PROJECT_ROOT)}')
    return x_train_path, y_train_path, x_test_path



def request_json(method: str, url: str, *, headers: dict[str, str], json: dict[str, Any] | None = None) -> dict[str, Any]:
    with httpx.Client(timeout=REQUEST_TIMEOUT, verify=resolve_requests_verify()) as client:
        response = client.request(method, url, headers=headers, json=json)
        response.raise_for_status()
        return response.json()



def upload_to_signed_url(path: Path, info: dict[str, Any]) -> None:
    signed_url = info['signed_urls'][0]
    required_headers = info.get('required_headers', {})
    with httpx.Client(timeout=REQUEST_TIMEOUT, verify=resolve_requests_verify()) as client:
        response = client.put(signed_url, content=path.read_bytes(), headers=required_headers)
        response.raise_for_status()



def run_priorlabs(token: str, x_train_path: Path, y_train_path: Path, x_test_path: Path) -> list[float]:
    headers = {'Authorization': f'Bearer {token}'}

    print('Checking Prior Labs model limits...')
    request_json('GET', f'{BASE_URL}/tabpfn/get_model_limits', headers=headers)

    train_prep = request_json(
        'POST',
        f'{BASE_URL}/tabpfn/prepare_train_set_upload',
        headers=headers,
        json={'x_train_info': {'format': 'csv'}, 'y_train_info': {'format': 'csv'}},
    )
    train_set_upload_id = train_prep['train_set_upload_id']
    upload_to_signed_url(x_train_path, train_prep['x_train_info'])
    upload_to_signed_url(y_train_path, train_prep['y_train_info'])

    fit_result = request_json(
        'POST',
        f'{BASE_URL}/tabpfn/fit',
        headers=headers,
        json={'train_set_upload_id': train_set_upload_id, 'task': 'regression'},
    )
    fitted_train_set_id = fit_result['fitted_train_set_id']

    test_prep = request_json(
        'POST',
        f'{BASE_URL}/tabpfn/prepare_test_set_upload',
        headers=headers,
        json={'fitted_train_set_id': fitted_train_set_id, 'x_test_info': {'format': 'csv'}},
    )
    test_set_upload_id = test_prep['test_set_upload_id']
    upload_to_signed_url(x_test_path, test_prep['x_test_info'])

    result = request_json(
        'POST',
        f'{BASE_URL}/tabpfn/predict',
        headers=headers,
        json={
            'test_set_upload_id': test_set_upload_id,
            'fitted_train_set_id': fitted_train_set_id,
            'task_config': {'task': 'regression', 'predict_params': {'output_type': 'mean'}},
        },
    )

    prediction = result['prediction']
    if isinstance(prediction, dict):
        for key in ['mean', 'predictions', 'values', 'data']:
            if key in prediction:
                prediction = prediction[key]
                break
    return [float(value) for value in prediction]



def merge_global_comparison(tabpfn_metrics: pd.DataFrame, tabpfn_predictions: pd.DataFrame) -> pd.DataFrame:
    if not LOCAL_METRICS_PATH.exists() or not LOCAL_PREDICTIONS_PATH.exists():
        raise SystemExit('Run scripts/08_train_baseline_models.py first.')

    local_metrics = pd.read_csv(LOCAL_METRICS_PATH)
    local_predictions = pd.read_csv(LOCAL_PREDICTIONS_PATH)
    comparison, all_predictions = merge_model_artifacts(local_metrics, local_predictions, tabpfn_metrics, tabpfn_predictions)
    comparison.to_csv(COMPARISON_PATH, index=False)
    all_predictions.to_csv(ALL_PREDICTIONS_PATH, index=False)
    return comparison



def write_outputs(predicted: list[float], y_test: pd.Series, metadata: pd.DataFrame) -> pd.DataFrame:
    predictions = metadata.copy()
    predictions['model'] = 'tabpfn_priorlabs'
    predictions['actual'] = y_test.values
    predictions['predicted'] = np.array(predicted)
    predictions['residual'] = predictions['actual'] - predictions['predicted']
    predictions['abs_error'] = predictions['residual'].abs()

    metrics = pd.DataFrame(
        [
            {
                'model': 'tabpfn_priorlabs',
                'dependency': 'priorlabs_api',
                'train_rows': None,
                'test_rows': len(predictions),
                'train_mae': None,
                'test_mae': float(predictions['abs_error'].mean()),
                'train_rmse': None,
                'test_rmse': rmse(predictions['actual'], predictions['predicted'].to_numpy()),
                'train_r2': None,
                'test_r2': float(1 - np.sum((predictions['actual'] - predictions['predicted']) ** 2) / np.sum((predictions['actual'] - predictions['actual'].mean()) ** 2)),
                'best_cv_mae': None,
            }
        ]
    )

    predictions.to_csv(TABLES_DIR / 'tabpfn_priorlabs_predictions.csv', index=False)
    metrics.to_csv(TABLES_DIR / 'tabpfn_priorlabs_metrics.csv', index=False)

    comparison = merge_global_comparison(metrics, predictions)

    plt.figure(figsize=(7, 7))
    plt.scatter(predictions['actual'], predictions['predicted'], s=18, alpha=0.55)
    low = min(predictions['actual'].min(), predictions['predicted'].min())
    high = max(predictions['actual'].max(), predictions['predicted'].max())
    plt.plot([low, high], [low, high], linestyle='--', linewidth=1)
    plt.xlabel('Actual life expectancy')
    plt.ylabel('Predicted life expectancy')
    plt.title('TabPFN via Prior Labs: actual vs predicted')
    savefig('09_tabpfn_actual_vs_predicted.png')

    plt.figure(figsize=(8.5, 5.2))
    plt.barh(comparison['model'], comparison['test_mae'])
    plt.gca().invert_yaxis()
    plt.xlabel('Test MAE')
    plt.title('Global model comparison including TabPFN reference')
    savefig('10_model_comparison_mae.png')

    print('\nTabPFN benchmark completed.')
    print(comparison[['model', 'test_mae', 'test_rmse', 'test_r2']].to_string(index=False))
    return comparison



def main() -> None:
    if not DATA_PATH.exists():
        raise SystemExit('Run scripts/06_audit_dataset_quality.py first.')
    if not LOCAL_METRICS_PATH.exists():
        raise SystemExit('Run scripts/08_train_baseline_models.py first.')

    token = load_api_key()
    if not token:
        print('PRIORLABS_API_KEY not found. Skipping optional TabPFN benchmark and keeping local comparison only.')
        return

    data = pd.read_csv(DATA_PATH)
    x_train, y_train, x_test, y_test, metadata = prepare_tabpfn_matrices(data)
    x_train_path, y_train_path, x_test_path = write_upload_files(x_train, y_train, x_test)
    predicted = run_priorlabs(token, x_train_path, y_train_path, x_test_path)

    if len(predicted) != len(y_test):
        raise SystemExit(f'Prediction length mismatch: got {len(predicted)}, expected {len(y_test)}')

    write_outputs(predicted, y_test, metadata)


if __name__ == '__main__':
    main()
