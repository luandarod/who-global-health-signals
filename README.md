# Global Health Signals

**A WHO country-year benchmark for explaining and predicting life expectancy differences with public health indicators.**

This repository is an end-to-end analytical project that rebuilds public WHO Global Health Observatory signals into a country-year panel, audits data quality, benchmarks multiple predictive models, analyzes residuals, and publishes the results as an interactive web report.

## Live report

Published site:

- [who-global-health-signals.vercel.app](https://who-global-health-signals.vercel.app)

## Executive summary

### Target question

Can public health indicators from the WHO Global Health Observatory explain observable variation and predict differences in life expectancy across countries?

### Short answer

Yes. On the current rebuilt panel, public WHO indicators provide a very strong predictive signal for life expectancy at birth.

On the temporal holdout beginning in 2015:

- The final global champion is `tabpfn_priorlabs` with `test_mae = 0.110`, `test_rmse = 0.170`, and `test_r2 = 0.9995`.
- The best local fully trainable model is `ridge` with `test_mae = 0.243`, followed closely by `elastic_net = 0.250`, `lightgbm = 0.250`, and `gradient_boosting = 0.251`.
- The gap between the external TabPFN reference and the best local model is real, but the more important conclusion is broader: the signal is strong across model families, not only in a single winner.

### Business-case interpretation

This means the public WHO indicator layer is already rich enough to support practical comparative monitoring of life expectancy differences. The project therefore answers the target question in two ways:

1. analytically, by showing that the panel predicts recent country-year life expectancy with low error
2. operationally, by showing that residuals identify where public indicators do not fully explain the observed outcome

In other words, the data is strong enough not only to describe the world, but also to support a useful benchmark for follow-up, exception handling, and decision intelligence.

## Main findings

### 1. The predictive signal is unusually strong

The current benchmark uses a country-year panel with:

- `13,785` rows and `34` columns in the full analytical dataset
- `4,048` rows and `31` columns in the modeling-ready dataset
- `218` countries or entities
- coverage from `1932` to `2024`
- a temporal split with `2,760` training rows and `1,288` test rows

Even after upstream quality controls and removal of incompatible stratified indicators, the surviving panel remains highly predictive.

### 2. Local trainable models are already credible

The local benchmark is not a toy baseline. It includes:

- `Ridge`
- `ElasticNet`
- `SVR`
- `KNN`
- `RandomForest`
- `ExtraTrees`
- `GradientBoosting`
- `HistGradientBoosting`
- `XGBoost` when installed
- `LightGBM` when installed
- `CatBoost` when installed

The current best local result, `ridge`, reaches `0.243` years of mean absolute error on the temporal holdout. That is materially worse than TabPFN, but still extremely strong for a global country-year health benchmark based on public indicators.

### 3. Residuals are still analytically valuable

High predictive fit does not eliminate uncertainty. It changes the role of the error term.

Current residual highlights:

- Lowest regional error: `Western Pacific`, `0.057`
- Highest regional error: `Eastern Mediterranean`, `0.129`
- Lowest yearly error in the holdout: `2015`, `0.035`
- Highest yearly error in the holdout: `2021`, `0.278`
- Largest positive residual: `IND 2021`, `+0.969`
- Largest negative residual: `SSD 2019`, `-0.600`
- Country with highest average test error: `SYR`, `0.385`

These cases are not causal proofs. They are follow-up signals. They tell us where country context, shocks, reporting asymmetries, or omitted structure may still matter.

### 4. The answer is stronger after the upstream audit, not weaker

During the audit and rebuild process, the project deliberately removed several failure modes:

- silent averaging across incompatible WHO strata
- ambiguous variable naming and collisions
- premature exclusion of otherwise useful variables
- unstable frontend narratives tied to outdated champions

As a result, the current answer is more trustworthy because it is based on a stricter dataset and a cleaner export chain.

## Final benchmark snapshot

As of **May 18, 2026**, the final comparison on the current dataset is:

| Model | Dependency | Test rows | Test MAE | Test RMSE | Test R2 |
|---|---|---:|---:|---:|---:|
| TabPFN / Prior Labs | `priorlabs_api` | 1,288 | 0.110 | 0.170 | 0.999 |
| Ridge | `local` | 1,288 | 0.243 | 0.304 | 0.998 |
| Elastic Net | `local` | 1,288 | 0.250 | 0.312 | 0.998 |
| LightGBM | `lightgbm` | 1,288 | 0.250 | 0.339 | 0.998 |
| Gradient Boosting | `local` | 1,288 | 0.251 | 0.343 | 0.998 |
| XGBoost | `xgboost` | 1,288 | 0.269 | 0.377 | 0.997 |
| Extra Trees | `local` | 1,288 | 0.313 | 0.436 | 0.997 |
| HistGradientBoosting | `local` | 1,288 | 0.319 | 0.420 | 0.997 |
| CatBoost | `catboost` | 1,288 | 0.338 | 0.445 | 0.996 |
| Random Forest | `local` | 1,288 | 0.365 | 0.500 | 0.995 |
| SVR RBF | `local` | 1,288 | 0.480 | 0.792 | 0.989 |
| KNN | `local` | 1,288 | 1.057 | 1.409 | 0.964 |

### How to read this table

- `MAE` is the main ranking metric because it is the most interpretable in years of life expectancy error.
- `RMSE` helps show whether some models carry heavier misses.
- `R2` confirms that the retained panel explains most of the observed variance.
- The best local benchmark matters because it is fully trainable and reproducible inside this repository.
- The TabPFN result matters because it is the strongest final accuracy result on the current rebuilt panel.

## Analytical design

### Unit of analysis

`country-year`

### Target

`life_expectancy_at_birth`

### Features

Health indicators plus temporal and data-quality context, including signals related to:

- mortality
- immunization
- health expenditure
- service coverage
- disease burden
- environmental and sanitation indicators
- reporting completeness

### Split strategy

- train on years before `2015`
- test on `2015` onward

This is important because it makes the benchmark forward-looking instead of mixing past and future observations randomly.

## Pipeline

```text
WHO GHO API
  ->
indicator discovery and shortlist
  ->
country-year dataset build
  ->
data quality audit
  ->
EDA and signal profiling
  ->
heavy local benchmark
  ->
optional TabPFN comparison
  ->
residual analysis and response surfaces
  ->
JSON asset export
  ->
interactive Astro report
```

## Repository structure

```text
who-global-health-signals/
|-- data/
|   |-- interim/
|   |-- processed/
|   `-- public/
|-- docs/
|-- notebooks/
|-- outputs/
|   |-- figures/
|   `-- tables/
|-- scripts/
|-- src/
|   |-- data/
|   `-- models/
|-- tests/
|-- web/
|-- .env.example
|-- .gitignore
|-- .nvmrc
|-- requirements.txt
|-- vercel.json
`-- README.md
```

## Core outputs

### Processed data

```text
data/processed/who_country_year_dataset.csv
data/processed/who_country_year_dataset.parquet
data/processed/who_country_year_modeling_ready.csv
data/processed/who_country_year_modeling_ready.parquet
```

### Report assets

```text
data/public/*.json
web/public/data/*.json
```

Important current web assets include:

- `report_summary.json`
- `model_comparison.json`
- `champion_predictions.json`
- `model_error_by_year.json`
- `region_residuals.json`
- `year_residuals.json`
- `country_residuals_top.json`
- `variable_coverage.json`
- `yearly_completeness.json`
- `life_expectancy_trends.json`
- `model_response_surfaces.json`

### Analytical tables

```text
outputs/tables/dataset_overview.csv
outputs/tables/variable_missingness.csv
outputs/tables/year_coverage.csv
outputs/tables/country_coverage.csv
outputs/tables/eda_key_findings.csv
outputs/tables/local_model_metrics.csv
outputs/tables/local_model_predictions.csv
outputs/tables/local_model_search_results.csv
outputs/tables/local_model_feature_importance.csv
outputs/tables/local_model_availability.csv
outputs/tables/local_model_surface_payload.json
outputs/tables/tabpfn_priorlabs_metrics.csv
outputs/tables/tabpfn_priorlabs_predictions.csv
outputs/tables/model_comparison_metrics.csv
outputs/tables/all_model_predictions.csv
outputs/tables/model_error_by_model.csv
outputs/tables/model_error_by_model_region.csv
outputs/tables/model_error_by_model_year.csv
outputs/tables/residuals_by_country.csv
outputs/tables/residuals_by_region.csv
outputs/tables/residuals_by_year.csv
outputs/tables/top_positive_residuals.csv
outputs/tables/top_negative_residuals.csv
outputs/tables/executive_findings.csv
```

### Figures

```text
outputs/figures/01_variable_coverage_top15.png
outputs/figures/02_yearly_data_completeness.png
outputs/figures/03_completeness_by_region.png
outputs/figures/04_life_expectancy_trend_by_region.png
outputs/figures/05_scatter_*_vs_life_expectancy.png
outputs/figures/06_champion_actual_vs_predicted.png
outputs/figures/07_champion_residuals_by_region.png
outputs/figures/08_champion_feature_importance.png
outputs/figures/09_tabpfn_actual_vs_predicted.png
outputs/figures/10_model_comparison_mae.png
outputs/figures/11_residuals_by_region.png
outputs/figures/12_residuals_by_year.png
outputs/figures/13_top_country_residuals.png
outputs/figures/14_local_model_comparison.png
outputs/figures/15_local_model_error_by_year.png
outputs/figures/16_response_surface_<model>.png
outputs/figures/17_response_surface_<model>.png
```

The site no longer depends on these PNG figures directly. They remain useful as static research artifacts, while the frontend now renders native charts from JSON payloads.

## Interactive report

The web report is designed as an editorial analytical experience rather than a classic BI dashboard.

Current frontend direction:

- an executive summary at the top
- a balanced answer to the target question
- native charts instead of embedded PNG figures
- a compact benchmark view by default, with full ranking available on demand
- glossary interactions for technical terms
- residual sections framed as investigative follow-up
- a separate model behavior section for response-surface evidence
- responsive sticky navigation tuned for section anchors across desktop and mobile

## WHO API and TLS notes

The WHO client now handles the certificate issue that previously blocked live access on Windows.

- By default, the client builds a CA bundle using the local Windows trust store plus `certifi`.
- Set `WHO_GHO_CA_BUNDLE=/path/to/bundle.pem` to force a custom trust bundle.
- Set `WHO_GHO_SSL_VERIFY=false` only as a debugging fallback.

Base endpoint:

```text
https://ghoapi.azureedge.net/api/
```

## Local development

### Python

Use your project Python environment and install from:

```text
requirements.txt
```

### Web

The Astro app is pinned and should be installed with:

```powershell
npm.cmd ci --prefix web
```

Use Node `22.12.0` or newer. The repository includes:

- `.nvmrc`
- `web/package.json` `engines`
- `web/package-lock.json`

To run the site locally:

```powershell
cd "C:\Users\Luanda Rodrigues\who-global-health-signals"
npm.cmd run dev --prefix .\web
```

To build the production site locally:

```powershell
$env:ASTRO_TELEMETRY_DISABLED='1'
npm.cmd run build --prefix .\web
```

To rebuild the web JSON assets after analytical changes:

```powershell
python scripts/10_analyze_model_residuals.py
python scripts/11_export_report_assets.py
python scripts/12_prepare_web_assets.py
```

## Interpretation guardrails

This repository supports a strong predictive answer, but there are still important limits:

- predictive fit is not the same thing as causal explanation
- the panel is only as strong as the retained public indicators
- residuals point to follow-up opportunities, not automatic policy conclusions
- some indicators remain historically uneven by region and period
- TabPFN is an external benchmark and requires sending prepared data to a third-party API

## What this repo now answers well

The project now answers the following with confidence:

1. whether a public WHO country-year indicator panel can predict life expectancy differences
2. which model families remain competitive under a forward-looking temporal split
3. which regions, years, and countries remain hardest to explain
4. how to turn the result into a reproducible analytical report instead of a notebook-only artifact

## Deployment

This repository is configured for Vercel with:

- `npm ci --prefix web` as the install command
- `npm run build --prefix web` as the build command
- `web/dist` as the static output directory

The current production shell is the same one described in this README:

- executive summary first
- native chart evidence throughout the report
- glossary support for non-technical readers
- benchmark, residuals, and model-behavior chapters

## Next high-value extensions

1. Add more explicit uncertainty language and calibration commentary around the champion benchmark.
2. Deepen the country case explorer with richer narrative follow-up for outlier cases.
3. Add robustness checks for alternative time cutoffs and feature-set stability.
4. Extend the native frontend chart layer with richer drill-down interaction where it improves interpretation.
