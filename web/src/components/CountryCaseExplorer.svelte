<script>
  import GlossaryTerm from './GlossaryTerm.svelte';
  import { formatNumber } from '../lib/presentation.js';

  export let countries = [];
  export let limit = 10;

  let selectedIndex = 0;

  $: rows = (countries ?? []).slice(0, limit);
  $: selected = rows[selectedIndex] ?? rows[0];

  function handleKeydown(event, index) {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      selectedIndex = index;
    }
  }
</script>

<section class="case-layout">
  <div class="case-grid">
    {#each rows as row, index}
      <article
        class:active={index === selectedIndex}
        class="case-card"
        role="button"
        tabindex="0"
        aria-pressed={index === selectedIndex}
        on:click={() => (selectedIndex = index)}
        on:keydown={(event) => handleKeydown(event, index)}
      >
        <span class="rank">#{String(index + 1).padStart(2, '0')}</span>
        <strong>{row.country_code}</strong>
        <span class="region">{row.region ?? 'Unknown region'}</span>
        <div class="case-metric"><span>mean error</span><b>{formatNumber(row.mean_abs_error, 2)}</b></div>
        <div class="case-metric"><span>residual</span><b>{formatNumber(row.mean_residual, 2)}</b></div>
      </article>
    {/each}
  </div>

  {#if selected}
    <aside class="detail">
      <span>Selected case</span>
      <strong>{selected.country_code}</strong>
      <h4>{selected.region ?? 'Unknown region'}</h4>
      <p>
        This country appears in the test window from {selected.min_year} to {selected.max_year}.
        Average <GlossaryTerm term="residual" label="residual" /> is {formatNumber(selected.mean_residual, 2)} years.
      </p>
      <p>
        Average error is {formatNumber(selected.mean_abs_error, 2)} years, with a maximum single-year miss of
        {formatNumber(selected.max_abs_error, 2)} years.
      </p>
      <p>
        Mean data <GlossaryTerm term="completeness" label="completeness" /> is
        {formatNumber((selected.mean_data_completeness ?? 0) * 100, 0)}%.
      </p>
    </aside>
  {/if}
</section>

<style>
  .case-layout {
    display: grid;
    grid-template-columns: minmax(0, 1fr) 280px;
    gap: 16px;
  }

  .case-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 10px;
  }

  .case-card {
    border: 1px solid rgba(247, 243, 232, 0.14);
    border-radius: 18px;
    padding: 14px;
    background: #090908;
    cursor: pointer;
    transition: border-color 0.18s ease, background 0.18s ease, transform 0.18s ease;
  }

  .case-card:hover,
  .case-card.active {
    border-color: rgba(215, 255, 111, 0.45);
    background: rgba(215, 255, 111, 0.055);
  }

  .case-card:hover {
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

  .detail {
    border: 1px solid rgba(247, 243, 232, 0.14);
    border-radius: 22px;
    padding: 18px;
    background: rgba(0, 0, 0, 0.24);
  }

  .detail span {
    color: #d7ff6f;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
  }

  .detail strong {
    margin-top: 14px;
    font-size: 38px;
  }

  .detail h4 {
    margin: 8px 0 12px;
    color: #d8d0c3;
    font-size: 16px;
  }

  .detail p {
    margin: 0 0 10px;
    color: #9d958b;
    font-size: 13px;
    line-height: 1.45;
  }

  @media (max-width: 1160px) {
    .case-layout,
    .case-grid {
      grid-template-columns: 1fr;
    }
  }
</style>
