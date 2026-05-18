<script>
  import GlossaryTerm from './GlossaryTerm.svelte';
  import { formatModelName, formatNumber } from '../lib/presentation.js';

  export let findings = [];

  const selectedIds = ['champion_model', 'overall_error', 'best_region', 'worst_region', 'worst_year', 'positive_outlier', 'negative_outlier'];

  $: rows = (findings ?? []).filter((finding) => selectedIds.includes(finding.finding_id));

  function valueLabel(finding) {
    if (finding.finding_id === 'champion_model') return formatModelName(finding.metric);
    return typeof finding.value === 'number' ? formatNumber(finding.value, 2) : finding.value;
  }

  function metricLabel(finding) {
    if (finding.finding_id === 'champion_model') return 'Best overall model';
    if (finding.finding_id === 'overall_error') return 'Champion MAE';
    return String(finding.metric);
  }
</script>

<div class="findings-grid">
  {#each rows as finding}
    <article>
      <strong>{valueLabel(finding)}</strong>
      <span>{metricLabel(finding)}</span>
      <p>{finding.finding}</p>
      {#if finding.finding_id === 'overall_error'}
        <p class="meta"><GlossaryTerm term="mae" label="MAE" /> reads average absolute prediction error on the holdout period.</p>
      {:else if finding.finding_id === 'positive_outlier' || finding.finding_id === 'negative_outlier'}
        <p class="meta"><GlossaryTerm term="outlier" label="Outlier" /> cases are starting points for deeper context review.</p>
      {/if}
    </article>
  {/each}
</div>

<style>
  .findings-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 14px;
  }

  article {
    min-height: 170px;
    border: 1px solid rgba(247, 243, 232, 0.14);
    border-radius: 22px;
    padding: 20px;
    background: #090908;
  }

  strong {
    display: block;
    color: #d7ff6f;
    font-size: 28px;
    letter-spacing: -0.035em;
    line-height: 1;
  }

  span {
    display: block;
    margin-top: 13px;
    color: #f7f3e8;
    font-size: 15px;
    font-weight: 800;
    line-height: 1.2;
  }

  p {
    margin: 8px 0 0;
    color: #9d958b;
    line-height: 1.4;
    font-size: 14px;
  }

  .meta {
    color: #8f887f;
  }

  @media (max-width: 1160px) {
    .findings-grid {
      grid-template-columns: 1fr;
    }
  }
</style>
