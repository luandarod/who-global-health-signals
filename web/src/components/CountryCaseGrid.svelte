<script>
  import { formatNumber } from '../lib/format.js';

  export let countries = [];
  export let limit = 10;

  let selectedIndex = 0;

  $: rows = (countries ?? []).slice(0, limit);
</script>

<div class="case-grid">
  {#each rows as row, index}
    <article class:active={index === selectedIndex} on:click={() => (selectedIndex = index)}>
      <span class="rank">#{String(index + 1).padStart(2, '0')}</span>
      <strong>{row.country_code}</strong>
      <span class="region">{row.region ?? 'Unknown region'}</span>
      <div class="case-metric"><span>mean error</span><b>{formatNumber(row.mean_abs_error, 2)}</b></div>
      <div class="case-metric"><span>residual</span><b>{formatNumber(row.mean_residual, 2)}</b></div>
    </article>
  {/each}
</div>

<style>
  .case-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 10px;
    padding: 0 22px 22px;
  }

  article {
    border: 1px solid rgba(247, 243, 232, 0.14);
    border-radius: 18px;
    padding: 14px;
    background: #090908;
    cursor: pointer;
    transition: border-color 0.18s ease, background 0.18s ease, transform 0.18s ease;
  }

  article:hover,
  article.active {
    border-color: rgba(215, 255, 111, 0.45);
    background: rgba(215, 255, 111, 0.055);
  }

  article:hover {
    transform: translateY(-1px);
  }

  .rank {
    color: #d7ff6f;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.12em;
  }

  strong {
    display: block;
    margin: 12px 0 5px;
    color: #f7f3e8;
    font-size: 26px;
    line-height: 0.95;
  }

  .region {
    display: block;
    color: #9d958b;
    font-size: 12px;
    line-height: 1.3;
  }

  .case-metric {
    display: flex;
    justify-content: space-between;
    gap: 10px;
    border-top: 1px solid rgba(247, 243, 232, 0.14);
    padding-top: 9px;
    margin-top: 10px;
  }

  .case-metric span {
    color: #9d958b;
    font-size: 12px;
  }

  .case-metric b {
    color: #f7f3e8;
    font-size: 13px;
  }

  @media (max-width: 1160px) {
    .case-grid {
      grid-template-columns: 1fr 1fr;
    }
  }

  @media (max-width: 720px) {
    .case-grid {
      grid-template-columns: 1fr;
    }
  }
</style>
