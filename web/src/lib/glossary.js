export const GLOSSARY = {
  country_year: {
    label: 'country-year',
    short: 'One country observed in one year.',
    long: 'A single record representing one country in one calendar year. This is the core unit used to train and evaluate the models in this report.'
  },
  benchmark: {
    label: 'benchmark',
    short: 'A side-by-side model comparison on the same task.',
    long: 'A structured comparison where multiple models solve the same prediction task under the same data split so performance differences are interpretable.'
  },
  temporal_split: {
    label: 'temporal split',
    short: 'Train on earlier years, test on later years.',
    long: 'A validation strategy that trains on older records and evaluates on newer ones. It is stricter than a random split because it better reflects forward-looking prediction.'
  },
  mae: {
    label: 'MAE',
    short: 'Average absolute prediction error.',
    long: 'Mean Absolute Error. It measures the average distance between predicted and observed life expectancy. Lower values indicate closer predictions.'
  },
  rmse: {
    label: 'RMSE',
    short: 'Error metric that penalizes larger misses more strongly.',
    long: 'Root Mean Squared Error. Like MAE, it measures prediction error, but it gives more weight to larger mistakes.'
  },
  r2: {
    label: 'R2',
    short: 'Share of variation explained by the model.',
    long: 'R-squared summarizes how much of the variation in observed life expectancy is captured by the model. Values closer to 1 indicate tighter fit.'
  },
  residual: {
    label: 'residual',
    short: 'Observed value minus predicted value.',
    long: 'The gap between observed and predicted life expectancy. Positive residuals mean observed life expectancy is above the model estimate; negative residuals mean it is below.'
  },
  coverage: {
    label: 'coverage',
    short: 'How often a variable is available in the dataset.',
    long: 'Coverage describes the share of country-year rows where a given indicator has a non-null value. Higher coverage usually means the signal is more broadly usable.'
  },
  completeness: {
    label: 'completeness',
    short: 'How much of the indicator set is present for a row or region.',
    long: 'Completeness describes how many expected indicators are available. In this report it helps explain where the modeling layer has stronger or weaker support.'
  },
  holdout: {
    label: 'holdout',
    short: 'Records reserved for final evaluation.',
    long: 'A portion of the data kept out of training and used only for evaluation. Here, the holdout period starts in 2015.'
  },
  predictive_signal: {
    label: 'predictive signal',
    short: 'Useful information that helps the model forecast life expectancy.',
    long: 'The part of the available indicators that consistently helps predict life expectancy differences across countries and years.'
  },
  outlier: {
    label: 'outlier',
    short: 'A case that stands apart from the general pattern.',
    long: 'A record or country whose residual is unusually large. Outliers can point to policy context, measurement limits, or changes the model does not summarize well.'
  }
};

export function getGlossaryTerm(term) {
  return GLOSSARY[term] ?? { label: term, short: '', long: '' };
}
