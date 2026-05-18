const FALLBACK = '-';

const MODEL_LABELS = {
  tabpfn_priorlabs: 'TabPFN (Prior Labs)',
  ridge: 'Ridge',
  elastic_net: 'Elastic Net',
  lightgbm: 'LightGBM',
  gradient_boosting: 'Gradient Boosting',
  xgboost: 'XGBoost',
  extra_trees: 'Extra Trees',
  hist_gradient_boosting: 'HistGradientBoosting',
  catboost: 'CatBoost',
  random_forest: 'Random Forest',
  svr_rbf: 'SVR (RBF)',
  knn: 'KNN'
};

const FEATURE_LABELS = {
  healthy_life_expectancy_hale_at_birth_years: 'Healthy life expectancy at birth',
  life_expectancy_at_age_60_years: 'Life expectancy at age 60',
  current_health_expenditure_percent_of_gdp: 'Current health expenditure (% of GDP)',
  domestic_general_government_health_expenditure_percent_of_gdp: 'Public health expenditure (% of GDP)',
  domestic_general_government_health_expenditure_percent_of_current_health_expenditure: 'Public share of health expenditure',
  population_using_safely_managed_drinking_water_services_percent: 'Safe drinking water access',
  population_using_safely_managed_sanitation_services_percent: 'Safe sanitation access',
  immunization_coverage_among_1_year_olds_dtp3_percent: 'DTP3 immunization coverage',
  under_five_mortality_rate_probability_of_dying_per_1000_live_births: 'Under-five mortality rate',
  neonatal_mortality_rate_per_1000_live_births: 'Neonatal mortality rate',
  maternal_mortality_ratio_per_100000_live_births: 'Maternal mortality ratio'
};

export function formatNumber(value, digits = 2) {
  const number = Number(value);
  if (!Number.isFinite(number)) return FALLBACK;
  return number.toLocaleString('en-US', { maximumFractionDigits: digits });
}

export function formatPercent(value, digits = 0) {
  const number = Number(value);
  if (!Number.isFinite(number)) return FALLBACK;
  return `${(number * 100).toLocaleString('en-US', { maximumFractionDigits: digits })}%`;
}

export function labelName(value) {
  return String(value ?? '')
    .replaceAll('_', ' ')
    .replace(/\b\w/g, (character) => character.toUpperCase());
}

export function compactLabel(value, max = 58) {
  const label = labelName(value);
  if (label.length <= max) return label;
  return `${label.slice(0, max - 3).trim()}...`;
}

export function formatYearRange(minYear, maxYear) {
  const start = Number.isFinite(Number(minYear)) ? String(minYear) : FALLBACK;
  const end = Number.isFinite(Number(maxYear)) ? String(maxYear) : FALLBACK;
  return `${start}-${end}`;
}

export function formatModelName(value) {
  return MODEL_LABELS[value] ?? labelName(value);
}

export function formatDependency(value) {
  if (value === 'priorlabs_api') return 'External reference';
  if (value === 'local') return 'Local benchmark';
  return labelName(value);
}

export function formatFeatureName(value) {
  const key = String(value ?? '').trim();
  if (!key) return FALLBACK;
  if (FEATURE_LABELS[key]) return FEATURE_LABELS[key];

  return key
    .replaceAll('_percent', ' percent')
    .replaceAll('_per_1000_live_births', ' per 1,000 live births')
    .replaceAll('_per_100000_live_births', ' per 100,000 live births')
    .replaceAll('_at_birth_years', ' at birth')
    .replaceAll('_years', '')
    .replaceAll('_', ' ')
    .replace(/\b\w/g, (character) => character.toUpperCase());
}
