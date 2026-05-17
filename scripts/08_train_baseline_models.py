"""Train baseline models for life expectancy prediction.

Run:
    python scripts/08_train_baseline_models.py

Outputs:
    outputs/tables/baseline_model_metrics.csv
    outputs/tables/baseline_model_predictions.csv
    outputs/tables/baseline_feature_importance.csv
    outputs/figures/06_baseline_actual_vs_predicted.png
    outputs/figures/07_baseline_residuals_by_region.png
    outputs/figures/08_baseline_feature_importance.png
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "who_country_year_modeling_ready.csv"
FIGURES_DIR = PROJECT_ROOT / "outputs" / "figures"
TABLES_DIR = PROJECT_ROOT / "outputs" / "tables"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)
TABLES_DIR.mkdir(parents=True, exist_ok=True)

TARGET = "life_expectancy_at_birth"
TEST_YEAR_MIN = 2015
RANDOM_STATE = 42


def savefig(name: str) -> None:
    path = FIGURES_DIR / name
    plt.tight_layout()
    plt.savefig(path, dpi=180, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path.relative_to(PROJECT_ROOT)}")


def rmse(y_true, y_pred) -> float:
    return float(np.sqrt(mean_squared_error(y_true, y_pred)))


def feature_sets(frame: pd.DataFrame) -> tuple[list[str], list[str]]:
    excluded = {"country_code", "region_code", "region", TARGET}
    numeric = [c for c in frame.columns if c not in excluded and pd.api.types.is_numeric_dtype(frame[c])]
    categorical = [c for c in ["region"] if c in frame.columns]
    return numeric, categorical


def preprocessor(numeric: list[str], categorical: list[str]) -> ColumnTransformer:
    num_pipe = Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())])
    cat_pipe = Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("onehot", OneHotEncoder(handle_unknown="ignore"))])
    return ColumnTransformer([("num", num_pipe, numeric), ("cat", cat_pipe, categorical)], remainder="drop")


def evaluate(name: str, model: Pipeline, train: pd.DataFrame, test: pd.DataFrame, features: list[str]) -> dict[str, object]:
    model.fit(train[features], train[TARGET])
    train_pred = model.predict(train[features])
    test_pred = model.predict(test[features])
    return {
        "model": name,
        "train_rows": len(train),
        "test_rows": len(test),
        "train_mae": mean_absolute_error(train[TARGET], train_pred),
        "test_mae": mean_absolute_error(test[TARGET], test_pred),
        "train_rmse": rmse(train[TARGET], train_pred),
        "test_rmse": rmse(test[TARGET], test_pred),
        "train_r2": r2_score(train[TARGET], train_pred),
        "test_r2": r2_score(test[TARGET], test_pred),
    }


def rf_importance(model: Pipeline, numeric: list[str], categorical: list[str]) -> pd.DataFrame:
    prep = model.named_steps["preprocessor"]
    reg = model.named_steps["model"]
    names = list(numeric)
    if categorical:
        onehot = prep.named_transformers_["cat"].named_steps["onehot"]
        names.extend(onehot.get_feature_names_out(categorical).tolist())
    return pd.DataFrame({"feature": names, "importance": reg.feature_importances_}).sort_values("importance", ascending=False)


def plot_outputs(predictions: pd.DataFrame, importance: pd.DataFrame) -> None:
    best = predictions[predictions["model"] == "random_forest"].copy()
    plt.figure(figsize=(7, 7))
    plt.scatter(best["actual"], best["predicted"], s=18, alpha=0.55)
    low = min(best["actual"].min(), best["predicted"].min())
    high = max(best["actual"].max(), best["predicted"].max())
    plt.plot([low, high], [low, high], linestyle="--", linewidth=1)
    plt.xlabel("Actual life expectancy")
    plt.ylabel("Predicted life expectancy")
    plt.title("Baseline model: actual vs predicted")
    savefig("06_baseline_actual_vs_predicted.png")

    residuals = best.groupby("region", dropna=False).agg(mean_abs_error=("abs_error", "mean")).reset_index().sort_values("mean_abs_error")
    plt.figure(figsize=(10, 5.5))
    plt.barh(residuals["region"].fillna("Unknown"), residuals["mean_abs_error"])
    plt.xlabel("Mean absolute error")
    plt.ylabel("WHO region")
    plt.title("Baseline prediction error by WHO region")
    savefig("07_baseline_residuals_by_region.png")

    top = importance.head(15).copy()
    top["label"] = top["feature"].str.replace("_", " ").str.wrap(36)
    plt.figure(figsize=(10, 7))
    plt.barh(top["label"], top["importance"])
    plt.gca().invert_yaxis()
    plt.xlabel("Random forest importance")
    plt.title("Top baseline predictors of life expectancy")
    savefig("08_baseline_feature_importance.png")


def main() -> None:
    if not DATA_PATH.exists():
        raise SystemExit("Run scripts/06_audit_dataset_quality.py first.")
    data = pd.read_csv(DATA_PATH)
    train = data[data["year"] < TEST_YEAR_MIN].copy()
    test = data[data["year"] >= TEST_YEAR_MIN].copy()
    numeric, categorical = feature_sets(data)
    features = numeric + categorical

    models = {
        "ridge": Pipeline([("preprocessor", preprocessor(numeric, categorical)), ("model", Ridge(alpha=1.0))]),
        "random_forest": Pipeline([("preprocessor", preprocessor(numeric, categorical)), ("model", RandomForestRegressor(n_estimators=300, min_samples_leaf=3, random_state=RANDOM_STATE, n_jobs=-1))]),
    }

    metrics = []
    preds = []
    fitted = {}
    for name, model in models.items():
        print(f"Training {name}...")
        metrics.append(evaluate(name, model, train, test, features))
        fitted[name] = model
        predicted = model.predict(test[features])
        frame = test[["country_code", "year", "region", TARGET]].copy()
        frame["model"] = name
        frame["predicted"] = predicted
        frame["actual"] = frame[TARGET]
        frame["residual"] = frame["actual"] - frame["predicted"]
        frame["abs_error"] = frame["residual"].abs()
        preds.append(frame)

    metrics_df = pd.DataFrame(metrics).sort_values("test_mae")
    predictions = pd.concat(preds, ignore_index=True)
    importance = rf_importance(fitted["random_forest"], numeric, categorical)

    metrics_df.to_csv(TABLES_DIR / "baseline_model_metrics.csv", index=False)
    predictions.to_csv(TABLES_DIR / "baseline_model_predictions.csv", index=False)
    importance.to_csv(TABLES_DIR / "baseline_feature_importance.csv", index=False)
    plot_outputs(predictions, importance)

    print("\nBaseline modeling completed.")
    print(metrics_df.to_string(index=False))


if __name__ == "__main__":
    main()
