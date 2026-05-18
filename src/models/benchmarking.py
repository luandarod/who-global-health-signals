"""Shared helpers for local benchmarking and analytical model surfaces."""

from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Callable

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import (
    ExtraTreesRegressor,
    GradientBoostingRegressor,
    HistGradientBoostingRegressor,
    RandomForestRegressor,
)
from sklearn.impute import SimpleImputer
from sklearn.linear_model import ElasticNet, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import RandomizedSearchCV
from sklearn.neighbors import KNeighborsRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import SVR

TARGET = 'life_expectancy_at_birth'
TEST_YEAR_MIN = 2015
RANDOM_STATE = 42


@dataclass(frozen=True)
class ModelSpec:
    name: str
    builder: Callable[[], object]
    search_space: dict[str, list[object]]
    scale_numeric: bool = True
    supports_feature_importance: bool = False
    dependency: str | None = None


@dataclass(frozen=True)
class SearchResult:
    model: str
    dependency: str | None
    best_cv_mae: float | None
    best_params: dict[str, object]


def merge_model_artifacts(
    primary_metrics: pd.DataFrame,
    primary_predictions: pd.DataFrame,
    secondary_metrics: pd.DataFrame | None = None,
    secondary_predictions: pd.DataFrame | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    metrics_frames = [primary_metrics]
    prediction_frames = [primary_predictions]

    if secondary_metrics is not None and not secondary_metrics.empty:
        metrics_frames.append(secondary_metrics)
    if secondary_predictions is not None and not secondary_predictions.empty:
        prediction_frames.append(secondary_predictions)

    comparison = pd.concat(metrics_frames, ignore_index=True).sort_values('test_mae').reset_index(drop=True)
    all_predictions = pd.concat(prediction_frames, ignore_index=True).reset_index(drop=True)
    return comparison, all_predictions



def rmse(y_true: pd.Series, y_pred: np.ndarray) -> float:
    return float(np.sqrt(mean_squared_error(y_true, y_pred)))



def feature_sets(frame: pd.DataFrame) -> tuple[list[str], list[str], list[str]]:
    excluded = {'country_code', 'region_code', 'region', TARGET}
    numeric = [c for c in frame.columns if c not in excluded and pd.api.types.is_numeric_dtype(frame[c])]
    categorical = [c for c in ['region'] if c in frame.columns]
    return numeric, categorical, numeric + categorical



def preprocessor(numeric: list[str], categorical: list[str], *, scale_numeric: bool = True) -> ColumnTransformer:
    num_steps: list[tuple[str, object]] = [('imputer', SimpleImputer(strategy='median'))]
    if scale_numeric:
        num_steps.append(('scaler', StandardScaler()))
    num_pipe = Pipeline(num_steps)
    cat_pipe = Pipeline(
        [
            ('imputer', SimpleImputer(strategy='most_frequent')),
            ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False)),
        ]
    )
    return ColumnTransformer([('num', num_pipe, numeric), ('cat', cat_pipe, categorical)], remainder='drop')



def temporal_train_test_split(frame: pd.DataFrame, *, test_year_min: int = TEST_YEAR_MIN) -> tuple[pd.DataFrame, pd.DataFrame]:
    train = frame.loc[frame['year'] < test_year_min].copy()
    test = frame.loc[frame['year'] >= test_year_min].copy()
    if train.empty or test.empty:
        raise ValueError('Train/test split produced an empty frame.')
    return train, test



def build_temporal_cv(train: pd.DataFrame, *, n_splits: int = 4) -> list[tuple[np.ndarray, np.ndarray]]:
    years = sorted(int(year) for year in train['year'].dropna().unique())
    if len(years) < 3:
        raise ValueError('Need at least three distinct train years for temporal CV.')

    validation_years = years[1:]
    n_splits = max(1, min(n_splits, len(validation_years)))
    splits: list[tuple[np.ndarray, np.ndarray]] = []
    for block in np.array_split(validation_years, n_splits):
        if len(block) == 0:
            continue
        block_years = [int(year) for year in block.tolist()]
        train_idx = np.flatnonzero(train['year'].to_numpy() < min(block_years))
        val_idx = np.flatnonzero(train['year'].isin(block_years).to_numpy())
        if len(train_idx) == 0 or len(val_idx) == 0:
            continue
        splits.append((train_idx, val_idx))

    if not splits:
        raise ValueError('Unable to build temporal CV splits from the train frame.')
    return splits



def _optional_model_specs() -> tuple[list[ModelSpec], list[dict[str, str]]]:
    specs: list[ModelSpec] = []
    missing: list[dict[str, str]] = []

    try:
        from xgboost import XGBRegressor

        specs.append(
            ModelSpec(
                name='xgboost',
                builder=lambda: XGBRegressor(
                    objective='reg:squarederror',
                    tree_method='hist',
                    random_state=RANDOM_STATE,
                    n_estimators=600,
                    learning_rate=0.05,
                    max_depth=6,
                    subsample=0.9,
                    colsample_bytree=0.9,
                    reg_lambda=1.0,
                    n_jobs=-1,
                ),
                search_space={
                    'model__n_estimators': [400, 600, 900],
                    'model__learning_rate': [0.03, 0.05, 0.08],
                    'model__max_depth': [3, 4, 6, 8],
                    'model__min_child_weight': [1, 3, 5],
                    'model__subsample': [0.7, 0.85, 1.0],
                    'model__colsample_bytree': [0.6, 0.8, 1.0],
                    'model__reg_lambda': [0.5, 1.0, 2.0, 5.0],
                },
                scale_numeric=False,
                supports_feature_importance=True,
                dependency='xgboost',
            )
        )
    except Exception as exc:  # noqa: BLE001
        missing.append({'model': 'xgboost', 'dependency': 'xgboost', 'reason': str(exc)})

    try:
        from lightgbm import LGBMRegressor

        specs.append(
            ModelSpec(
                name='lightgbm',
                builder=lambda: LGBMRegressor(
                    objective='regression',
                    random_state=RANDOM_STATE,
                    verbosity=-1,
                    n_estimators=800,
                    learning_rate=0.05,
                    n_jobs=-1,
                ),
                search_space={
                    'model__n_estimators': [500, 800, 1200],
                    'model__learning_rate': [0.03, 0.05, 0.08],
                    'model__num_leaves': [15, 31, 63, 127],
                    'model__max_depth': [-1, 4, 6, 8],
                    'model__min_child_samples': [5, 10, 20, 40],
                    'model__subsample': [0.7, 0.85, 1.0],
                    'model__colsample_bytree': [0.6, 0.8, 1.0],
                    'model__reg_lambda': [0.0, 0.5, 1.0, 3.0],
                },
                scale_numeric=False,
                supports_feature_importance=True,
                dependency='lightgbm',
            )
        )
    except Exception as exc:  # noqa: BLE001
        missing.append({'model': 'lightgbm', 'dependency': 'lightgbm', 'reason': str(exc)})

    try:
        from catboost import CatBoostRegressor

        specs.append(
            ModelSpec(
                name='catboost',
                builder=lambda: CatBoostRegressor(
                    loss_function='RMSE',
                    random_seed=RANDOM_STATE,
                    verbose=False,
                    allow_writing_files=False,
                    iterations=900,
                    learning_rate=0.05,
                    depth=6,
                ),
                search_space={
                    'model__iterations': [500, 900, 1400],
                    'model__learning_rate': [0.03, 0.05, 0.08],
                    'model__depth': [4, 6, 8, 10],
                    'model__l2_leaf_reg': [1.0, 3.0, 5.0, 9.0],
                    'model__bagging_temperature': [0.0, 0.5, 1.0],
                },
                scale_numeric=False,
                supports_feature_importance=True,
                dependency='catboost',
            )
        )
    except Exception as exc:  # noqa: BLE001
        missing.append({'model': 'catboost', 'dependency': 'catboost', 'reason': str(exc)})

    return specs, missing



def build_local_model_specs() -> tuple[list[ModelSpec], list[dict[str, str]]]:
    specs = [
        ModelSpec(
            name='ridge',
            builder=lambda: Ridge(random_state=RANDOM_STATE),
            search_space={'model__alpha': [0.01, 0.1, 1.0, 5.0, 10.0, 25.0, 50.0]},
        ),
        ModelSpec(
            name='elastic_net',
            builder=lambda: ElasticNet(random_state=RANDOM_STATE, max_iter=10000),
            search_space={
                'model__alpha': [0.001, 0.01, 0.1, 1.0, 3.0],
                'model__l1_ratio': [0.05, 0.2, 0.5, 0.8, 0.95],
            },
        ),
        ModelSpec(
            name='svr_rbf',
            builder=lambda: SVR(kernel='rbf'),
            search_space={
                'model__C': [0.5, 1.0, 3.0, 10.0, 30.0],
                'model__gamma': ['scale', 'auto', 0.03, 0.08, 0.15],
                'model__epsilon': [0.05, 0.1, 0.2, 0.4],
            },
        ),
        ModelSpec(
            name='knn',
            builder=lambda: KNeighborsRegressor(),
            search_space={
                'model__n_neighbors': [5, 7, 9, 11, 15, 21],
                'model__weights': ['uniform', 'distance'],
                'model__p': [1, 2],
            },
        ),
        ModelSpec(
            name='random_forest',
            builder=lambda: RandomForestRegressor(random_state=RANDOM_STATE, n_jobs=-1),
            search_space={
                'model__n_estimators': [300, 600, 900],
                'model__max_depth': [None, 8, 12, 18, 26],
                'model__min_samples_split': [2, 4, 8, 16],
                'model__min_samples_leaf': [1, 2, 4, 8],
                'model__max_features': [0.5, 0.7, 1.0, 'sqrt'],
            },
            scale_numeric=False,
            supports_feature_importance=True,
        ),
        ModelSpec(
            name='extra_trees',
            builder=lambda: ExtraTreesRegressor(random_state=RANDOM_STATE, n_jobs=-1),
            search_space={
                'model__n_estimators': [400, 700, 1000],
                'model__max_depth': [None, 8, 12, 18, 26],
                'model__min_samples_split': [2, 4, 8, 16],
                'model__min_samples_leaf': [1, 2, 4, 8],
                'model__max_features': [0.5, 0.7, 1.0, 'sqrt'],
            },
            scale_numeric=False,
            supports_feature_importance=True,
        ),
        ModelSpec(
            name='gradient_boosting',
            builder=lambda: GradientBoostingRegressor(random_state=RANDOM_STATE),
            search_space={
                'model__n_estimators': [200, 400, 700],
                'model__learning_rate': [0.03, 0.05, 0.08, 0.12],
                'model__max_depth': [2, 3, 4],
                'model__min_samples_leaf': [1, 3, 6, 10],
                'model__subsample': [0.7, 0.85, 1.0],
            },
            scale_numeric=False,
            supports_feature_importance=True,
        ),
        ModelSpec(
            name='hist_gradient_boosting',
            builder=lambda: HistGradientBoostingRegressor(random_state=RANDOM_STATE),
            search_space={
                'model__learning_rate': [0.03, 0.05, 0.08, 0.12],
                'model__max_depth': [None, 4, 6, 8],
                'model__max_leaf_nodes': [15, 31, 63, 127],
                'model__min_samples_leaf': [10, 20, 40, 80],
                'model__l2_regularization': [0.0, 0.1, 0.5, 1.0],
            },
            scale_numeric=False,
            supports_feature_importance=True,
        ),
    ]
    optional_specs, missing = _optional_model_specs()
    return specs + optional_specs, missing



def make_model_pipeline(spec: ModelSpec, numeric: list[str], categorical: list[str]) -> Pipeline:
    return Pipeline([
        ('preprocessor', preprocessor(numeric, categorical, scale_numeric=spec.scale_numeric)),
        ('model', spec.builder()),
    ])



def fit_with_search(
    spec: ModelSpec,
    train: pd.DataFrame,
    features: list[str],
    *,
    n_iter: int,
    cv_splits: list[tuple[np.ndarray, np.ndarray]],
) -> tuple[Pipeline, SearchResult]:
    pipeline = make_model_pipeline(spec, *feature_sets(train)[:2])
    search = RandomizedSearchCV(
        estimator=pipeline,
        param_distributions=spec.search_space,
        n_iter=min(n_iter, max(1, np.prod([len(values) for values in spec.search_space.values()]))),
        scoring='neg_mean_absolute_error',
        cv=cv_splits,
        random_state=RANDOM_STATE,
        n_jobs=1,
        refit=True,
        error_score='raise',
    )
    search.fit(train[features], train[TARGET])
    best_pipeline: Pipeline = search.best_estimator_
    result = SearchResult(
        model=spec.name,
        dependency=spec.dependency,
        best_cv_mae=float(-search.best_score_),
        best_params={key: value for key, value in search.best_params_.items()},
    )
    return best_pipeline, result



def evaluate_model(name: str, model: Pipeline, train: pd.DataFrame, test: pd.DataFrame, features: list[str]) -> tuple[dict[str, object], pd.DataFrame]:
    train_pred = model.predict(train[features])
    test_pred = model.predict(test[features])
    metrics = {
        'model': name,
        'train_rows': len(train),
        'test_rows': len(test),
        'train_mae': mean_absolute_error(train[TARGET], train_pred),
        'test_mae': mean_absolute_error(test[TARGET], test_pred),
        'train_rmse': rmse(train[TARGET], np.asarray(train_pred)),
        'test_rmse': rmse(test[TARGET], np.asarray(test_pred)),
        'train_r2': r2_score(train[TARGET], train_pred),
        'test_r2': r2_score(test[TARGET], test_pred),
    }
    frame = test[['country_code', 'year', 'region', TARGET]].copy()
    frame['model'] = name
    frame['predicted'] = np.asarray(test_pred)
    frame['actual'] = frame[TARGET]
    frame['residual'] = frame['actual'] - frame['predicted']
    frame['abs_error'] = frame['residual'].abs()
    return metrics, frame



def feature_names_from_pipeline(model: Pipeline, numeric: list[str], categorical: list[str]) -> list[str]:
    prep = model.named_steps['preprocessor']
    names = list(numeric)
    if categorical:
        onehot = prep.named_transformers_['cat'].named_steps['onehot']
        names.extend(onehot.get_feature_names_out(categorical).tolist())
    return names



def extract_feature_importance(model_name: str, model: Pipeline, numeric: list[str], categorical: list[str]) -> pd.DataFrame:
    estimator = model.named_steps['model']
    names = feature_names_from_pipeline(model, numeric, categorical)

    if hasattr(estimator, 'feature_importances_'):
        values = np.asarray(estimator.feature_importances_, dtype=float)
        importance_type = 'feature_importance'
    elif hasattr(estimator, 'coef_'):
        values = np.abs(np.ravel(np.asarray(estimator.coef_, dtype=float)))
        importance_type = 'abs_coefficient'
    else:
        return pd.DataFrame()

    if len(values) != len(names):
        return pd.DataFrame()

    return (
        pd.DataFrame({'model': model_name, 'feature': names, 'importance': values, 'importance_type': importance_type})
        .sort_values('importance', ascending=False)
        .reset_index(drop=True)
    )



def choose_surface_features(
    frame: pd.DataFrame,
    importance: pd.DataFrame | None = None,
    *,
    fallback_limit: int = 6,
) -> tuple[str, str]:
    numeric, _, _ = feature_sets(frame)
    numeric = [feature for feature in numeric if feature != 'year']
    ranked: list[str] = []

    if importance is not None and not importance.empty:
        for feature in importance['feature'].tolist():
            if feature in numeric and feature not in ranked:
                ranked.append(feature)
            if len(ranked) >= 2:
                break

    if len(ranked) < 2:
        correlations: list[tuple[str, float]] = []
        for feature in numeric:
            feature_frame = frame[[feature, TARGET]].dropna()
            if len(feature_frame) < fallback_limit:
                continue
            corr = feature_frame[feature].corr(feature_frame[TARGET])
            if pd.notna(corr):
                correlations.append((feature, abs(float(corr))))
        correlations.sort(key=lambda item: item[1], reverse=True)
        for feature, _ in correlations:
            if feature not in ranked:
                ranked.append(feature)
            if len(ranked) >= 2:
                break

    if len(ranked) < 2:
        raise ValueError('Unable to select two numeric surface features.')
    return ranked[0], ranked[1]



def build_surface_frame(
    model: Pipeline,
    reference_frame: pd.DataFrame,
    *,
    feature_x: str,
    feature_y: str,
    grid_size: int = 28,
    support_quantile: float = 0.9,
) -> tuple[pd.DataFrame, dict[str, object]]:
    numeric, categorical, features = feature_sets(reference_frame)
    baseline: dict[str, object] = {}
    for column in numeric:
        baseline[column] = float(reference_frame[column].median())
    for column in categorical:
        mode = reference_frame[column].mode(dropna=True)
        baseline[column] = None if mode.empty else mode.iloc[0]

    x_values = np.linspace(reference_frame[feature_x].quantile(0.05), reference_frame[feature_x].quantile(0.95), grid_size)
    y_values = np.linspace(reference_frame[feature_y].quantile(0.05), reference_frame[feature_y].quantile(0.95), grid_size)

    rows: list[dict[str, object]] = []
    for x_value in x_values:
        for y_value in y_values:
            row = dict(baseline)
            row[feature_x] = float(x_value)
            row[feature_y] = float(y_value)
            rows.append(row)

    surface = pd.DataFrame(rows)
    predicted = np.asarray(model.predict(surface[features]), dtype=float)

    observed = reference_frame[[feature_x, feature_y]].dropna().to_numpy(dtype=float)
    masked_share = 0.0
    if len(observed) >= 3:
        center = observed.mean(axis=0)
        scale = observed.std(axis=0)
        scale = np.where(scale == 0, 1.0, scale)

        observed_scaled = (observed - center) / scale
        grid_points = surface[[feature_x, feature_y]].to_numpy(dtype=float)
        grid_scaled = (grid_points - center) / scale

        observed_pairwise = np.sqrt(((observed_scaled[:, None, :] - observed_scaled[None, :, :]) ** 2).sum(axis=2))
        np.fill_diagonal(observed_pairwise, np.inf)
        neighbor_radius = observed_pairwise.min(axis=1)
        support_radius = float(max(np.quantile(neighbor_radius, support_quantile) * 1.75, 0.35))

        grid_distances = np.sqrt(((grid_scaled[:, None, :] - observed_scaled[None, :, :]) ** 2).sum(axis=2))
        nearest_observed = grid_distances.min(axis=1)
        supported = nearest_observed <= support_radius
        predicted = np.where(supported, predicted, np.nan)
        masked_share = float((~supported).mean())

    surface['predicted'] = predicted
    surface = surface[[feature_x, feature_y, 'predicted']]
    meta = {
        'feature_x': feature_x,
        'feature_y': feature_y,
        'grid_size': grid_size,
        'reference_region': baseline.get('region'),
        'reference_values': {key: value for key, value in baseline.items() if key not in {feature_x, feature_y}},
        'x_values': [float(value) for value in x_values.tolist()],
        'y_values': [float(value) for value in y_values.tolist()],
        'masked_share': masked_share,
    }
    return surface, meta



def surface_payload(model_name: str, surface: pd.DataFrame, meta: dict[str, object]) -> dict[str, object]:
    feature_x = str(meta['feature_x'])
    feature_y = str(meta['feature_y'])
    matrix = (
        surface.pivot(index=feature_y, columns=feature_x, values='predicted')
        .sort_index(axis=0)
        .sort_index(axis=1)
    )
    return {
        'model': model_name,
        'feature_x': feature_x,
        'feature_y': feature_y,
        'grid_size': int(meta['grid_size']),
        'reference_region': meta.get('reference_region'),
        'reference_values': meta.get('reference_values', {}),
        'x': [float(value) for value in matrix.columns.tolist()],
        'y': [float(value) for value in matrix.index.tolist()],
        'z': [[float(value) for value in row] for row in matrix.to_numpy().tolist()],
    }



def json_ready_search_results(results: list[SearchResult]) -> pd.DataFrame:
    rows = []
    for result in results:
        rows.append(
            {
                'model': result.model,
                'dependency': result.dependency,
                'best_cv_mae': result.best_cv_mae,
                'best_params_json': json.dumps(result.best_params, ensure_ascii=False, sort_keys=True),
            }
        )
    return pd.DataFrame(rows)
