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
