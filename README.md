# Global Health Signals

**Predicting health-system outcomes from WHO Global Health Observatory data using TabPFN.**

This repository is an end-to-end analytical project combining public health data, data quality analysis, machine learning and an interactive report.

## Analytical question

Can public health indicators from the WHO Global Health Observatory explain and predict differences in life expectancy across countries?

The first target outcome is **life expectancy at birth**. The analytical dataset is built as a country-year table using selected indicators from the WHO GHO OData API.

## Current result

The first modeling round shows that TabPFN via Prior Labs substantially outperformed the baseline models on the 2015+ temporal test set.

| Model | Test rows | Test MAE | Test RMSE | Test R² |
|---|---:|---:|---:|---:|
| TabPFN / Prior Labs | 1,288 | 0.938 | 1.520 | 0.958 |
| Random Forest | 1,288 | 1.876 | 2.533 | 0.883 |
| Ridge Regression | 1,288 | 2.815 | 3.637 | 0.758 |

Interpretation: using WHO health-system indicators, the TabPFN model predicted life expectancy with an average absolute error below one year on recent country-year records.

## Dataset snapshot

| Layer | Result |
|---|---:|
| Full analytical dataset | 13,838 rows × 46 columns |
| Countries / entities | 218 |
| Time range | 1932–2024 |
| Indicator columns | 39 |
| Modeling-ready dataset | 4,043 rows × 13 columns |
| Train set | 2,755 rows |
| Test set | 1,288 rows |

## Core hypotheses

1. Maternal, neonatal and under-5 mortality indicators are strong predictors of life expectancy.
2. Service coverage, immunization and UHC-related indicators are associated with higher life expectancy.
3. Environmental risks and sanitation indicators explain part of the variation between countries and regions.
4. Data availability itself is a signal: countries with lower reporting completeness may show weaker monitoring capacity.
5. Model residuals can highlight countries that perform better or worse than expected given their health-system profile.
6. Countries can be grouped into interpretable health-system profiles using coverage, mortality, environmental and data-quality signals.

## Pipeline

```text
WHO GHO API
   ↓
Indicator discovery and coverage profiling
   ↓
Country-year analytical dataset
   ↓
Missingness and data-quality audit
   ↓
EDA figures and key findings
   ↓
Baseline models: Ridge + Random Forest
   ↓
Prior Labs / TabPFN regression
   ↓
Model comparison and residual analysis
   ↓
Interactive report layer
```

## Generated outputs

### Data

```text
data/processed/who_country_year_dataset.csv
data/processed/who_country_year_dataset.parquet
data/processed/who_country_year_modeling_ready.csv
data/processed/who_country_year_modeling_ready.parquet
```

### Tables

```text
outputs/tables/dataset_overview.csv
outputs/tables/variable_missingness.csv
outputs/tables/year_coverage.csv
outputs/tables/country_coverage.csv
outputs/tables/eda_key_findings.csv
outputs/tables/baseline_model_metrics.csv
outputs/tables/baseline_model_predictions.csv
outputs/tables/baseline_feature_importance.csv
outputs/tables/tabpfn_priorlabs_metrics.csv
outputs/tables/tabpfn_priorlabs_predictions.csv
outputs/tables/model_comparison_metrics.csv
```

### Figures

```text
outputs/figures/01_variable_coverage_top15.png
outputs/figures/02_yearly_data_completeness.png
outputs/figures/03_completeness_by_region.png
outputs/figures/04_life_expectancy_trend_by_region.png
outputs/figures/05_scatter_*_vs_life_expectancy.png
outputs/figures/06_baseline_actual_vs_predicted.png
outputs/figures/07_baseline_residuals_by_region.png
outputs/figures/08_baseline_feature_importance.png
outputs/figures/09_tabpfn_actual_vs_predicted.png
outputs/figures/10_model_comparison_mae.png
```

## Project structure

```text
who-global-health-signals/
├── data/
│   ├── raw/
│   ├── interim/
│   ├── processed/
│   └── public/
├── notebooks/
├── outputs/
│   ├── figures/
│   └── tables/
├── reports/
├── scripts/
├── src/
│   ├── data/
│   ├── models/
│   ├── utils/
│   └── viz/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Data source

WHO Global Health Observatory OData API.

Base endpoint:

```text
https://ghoapi.azureedge.net/api/
```

## Modeling task

```text
target = life_expectancy_at_birth
unit = country-year
features = health indicators + temporal features + data quality metrics
split = train before 2015, test from 2015 onward
```

Models implemented:

- Ridge Regression.
- Random Forest Regressor.
- Prior Labs / TabPFN regression.

## Report direction

The final report should not look like a traditional BI dashboard. It will be an editorial analytical report with:

- Large visual chapters.
- Scroll-driven sections.
- Static charts for methodological clarity.
- Animated/interactive graphics for exploration.
- Clear executive conclusions.

Working title:

> **Global Health Signals: from public health indicators to decision intelligence**

## Next steps

1. Analyze TabPFN residuals by country, region and year.
2. Generate a first executive findings table.
3. Create public JSON files for the interactive report layer.
4. Build the web report with a scrollytelling interface.
5. Add model limitations and methodological notes.
