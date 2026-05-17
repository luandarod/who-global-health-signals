# Global Health Signals

**Predicting health-system outcomes from WHO Global Health Observatory data using TabPFN.**

This repository will become an end-to-end analytical project combining public health data, data quality analysis, machine learning and an interactive report.

## Analytical question

Can public health indicators from the WHO Global Health Observatory explain and predict differences in life expectancy across countries?

The first target outcome is **life expectancy at birth**. The analytical dataset will be built as a country-year table using selected indicators from the WHO GHO OData API.

## Core hypotheses

1. Maternal, neonatal and under-5 mortality indicators are strong predictors of life expectancy.
2. Service coverage, immunization and UHC-related indicators are associated with higher life expectancy.
3. Environmental risks and sanitation indicators explain part of the variation between countries and regions.
4. Data availability itself is a signal: countries with lower reporting completeness may show weaker monitoring capacity.
5. Model residuals can highlight countries that perform better or worse than expected given their health-system profile.
6. Countries can be grouped into interpretable health-system profiles using coverage, mortality, environmental and data-quality signals.

## Planned outputs

- WHO GHO extraction pipeline.
- Clean country-year analytical dataset.
- Data-quality layer with completeness, missingness and last-reported-year metrics.
- Exploratory analysis with static and animated charts.
- Baseline models and Prior Labs / TabPFN modeling.
- Model evaluation, residual analysis and feature interpretation.
- Interactive scrollytelling report built for the web.
- Technical methodology document.

## Initial project structure

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

## Modeling direction

The first modeling task will be regression:

```text
target = life_expectancy_at_birth
unit = country-year
features = health indicators + temporal features + data quality metrics
```

Models planned:

- Linear regression baseline.
- Random forest baseline.
- Prior Labs / TabPFN model.

## Report direction

The final report should not look like a traditional BI dashboard. It will be an editorial analytical report with:

- Large visual chapters.
- Scroll-driven sections.
- Static charts for methodological clarity.
- Animated/interactive graphics for exploration.
- Clear executive conclusions.

Working title:

> **Global Health Signals: from public health indicators to decision intelligence**

## Current status

Project scaffold created. Next step: explore the WHO GHO API and choose the first indicator set.
