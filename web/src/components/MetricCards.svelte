<script>
  import { formatNumber } from '../lib/format.js';

  export let summary = null;

  $: metrics = summary
    ? [
        {
          value: formatNumber(summary.dataset?.full_rows, 0),
          label: 'country-year rows',
          note: 'Full analytical table before modeling filter'
        },
        {
          value: formatNumber(summary.dataset?.countries, 0),
          label: 'countries/entities',
          note: 'Geographic units represented in WHO data'
        },
        {
          value: `${summary.dataset?.min_year ?? '—'}–${summary.dataset?.max_year ?? '—'}`,
          label: 'historical range',
          note: 'Longitudinal coverage available in the source table'
        },
        {
          value: formatNumber(summary.best_model?.test_mae, 2),
          label: 'TabPFN MAE years',
          note: 'Average absolute prediction error on recent test records'
        }
      ]
    : [];
</script>

<div class="metric-grid">
  {#each metrics as metric}
    <article class="metric-card">
      <strong>{metric.value}</strong>
      <span>{metric.label}</span>
      <p>{metric.note}</p>
    </article>
  {/each}
</div>

<style>
  .metric-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-bottom: 14px;
  }

  .metric-card {
    min-height: 142px;
    border: 1px solid rgba(247, 243, 232, 0.14);
    border-radius: 24px;
    padding: 20px;
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.055), rgba(255, 255, 255, 0.015));
  }

  strong {
    display: block;
    color: #f7f3e8;
    font-size: clamp(32px, 3.6vw, 54px);
    line-height: 0.95;
    letter-spacing: -0.04em;
    font-weight: 900;
  }

  span {
    display: block;
    margin-top: 12px;
    color: #9d958b;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
  }

  p {
    margin: 12px 0 0;
    color: #8f887f;
    font-size: 13px;
    line-height: 1.35;
  }

  @media (max-width: 1160px) {
    .metric-grid {
      grid-template-columns: 1fr 1fr;
    }
  }

  @media (max-width: 720px) {
    .metric-grid {
      grid-template-columns: 1fr;
    }
  }
</style>
