<script>
  import { formatNumber } from '../lib/format.js';

  export let findings = [];

  const selectedIds = ['overall_error', 'best_region', 'worst_region', 'worst_year', 'positive_outlier', 'negative_outlier'];
  $: rows = (findings ?? []).filter((finding) => selectedIds.includes(finding.finding_id));

  function valueLabel(value) {
    return typeof value === 'number' ? formatNumber(value, 2) : value;
  }
</script>

<div class="findings-grid">
  {#each rows as finding}
    <article>
      <strong>{valueLabel(finding.value)}</strong>
      <span>{finding.metric}</span>
      <p>{finding.finding}</p>
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
    min-height: 150px;
    border: 1px solid rgba(247, 243, 232, 0.14);
    border-radius: 22px;
    padding: 20px;
    background: #090908;
  }

  strong {
    display: block;
    color: #d7ff6f;
    font-size: 32px;
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

  @media (max-width: 1160px) {
    .findings-grid {
      grid-template-columns: 1fr;
    }
  }
</style>
