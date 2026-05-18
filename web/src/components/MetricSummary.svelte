<script>
  import GlossaryTerm from './GlossaryTerm.svelte';
  import { formatModelName, formatNumber, formatYearRange } from '../lib/presentation.js';

  export let summary = null;

  $: championName = formatModelName(summary?.best_model?.name);
  $: metrics = summary
    ? [
        {
          value: formatNumber(summary.dataset?.full_rows, 0),
          label: 'country-year rows',
          term: 'country_year',
          note: 'Full analytical table before the modeling filter.'
        },
        {
          value: formatNumber(summary.dataset?.countries, 0),
          label: 'countries and entities',
          note: 'Geographic units represented in the WHO source layer.'
        },
        {
          value: formatYearRange(summary.dataset?.min_year, summary.dataset?.max_year),
          label: 'historical range',
          note: 'Observed longitudinal range available in the analytical dataset.'
        },
        {
          value: formatNumber(summary.best_model?.test_mae, 2),
          label: `${championName} MAE`,
          term: 'mae',
          note: 'Average absolute prediction error on the temporal holdout.'
        }
      ]
    : [];
</script>

<div class="metric-grid">
  {#each metrics as metric}
    <article class="metric-card">
      <strong>{metric.value}</strong>
      <span>
        {metric.label}
        {#if metric.term}
          <GlossaryTerm term={metric.term} />
        {/if}
      </span>
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
    min-height: 154px;
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
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    align-items: center;
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
    line-height: 1.4;
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
