<script>
  import { barWidth } from '../lib/chartScales.js';
  import { compactLabel, formatNumber, formatPercent, labelName } from '../lib/format.js';

  export let title = '';
  export let description = '';
  export let data = [];
  export let labelKey = 'label';
  export let valueKey = 'value';
  export let mode = 'number';
  export let detailTitle = 'Selected signal';
  export let detailKind = 'generic';
  export let limit = 10;

  let selectedIndex = 0;
  let pointer = null;

  $: rows = (data ?? []).slice(0, limit);
  $: maxValue = Math.max(...rows.map((row) => Number(row[valueKey]) || 0), 0.01);
  $: selected = rows[selectedIndex] ?? rows[0];

  function formatValue(value) {
    return mode === 'percent' ? formatPercent(value) : formatNumber(value, 2);
  }

  function detailText(row) {
    if (!row) return '';

    if (detailKind === 'coverage') {
      return `Coverage in the country-year table: ${formatPercent(row.non_null_share)}. Missing share: ${formatPercent(row.missing_share)}.`;
    }

    if (detailKind === 'completeness') {
      return `Average data completeness across ${formatNumber(row.countries, 0)} countries and ${formatNumber(row.rows, 0)} country-year rows.`;
    }

    if (detailKind === 'residual') {
      return `Mean absolute prediction error: ${formatNumber(row.mean_abs_error, 2)} years. Rows: ${formatNumber(row.rows, 0)}. Countries: ${formatNumber(row.countries, 0)}.`;
    }

    return `${labelName(row[labelKey])}: ${formatValue(row[valueKey])}.`;
  }

  function showPointer(event, row) {
    pointer = {
      x: event.clientX,
      y: event.clientY,
      title: labelName(row[labelKey]),
      text: detailText(row)
    };
  }
</script>

<section class="chart-card">
  <header>
    <div>
      <h3>{title}</h3>
      <p>{description}</p>
    </div>
    <span class="micro">click to inspect</span>
  </header>

  <div class="chart-body">
    <div class="rows">
      {#each rows as row, index}
        <div
          class:active={index === selectedIndex}
          class="row"
          role="button"
          tabindex="0"
          on:click={() => (selectedIndex = index)}
          on:keydown={(event) => event.key === 'Enter' && (selectedIndex = index)}
          on:mousemove={(event) => showPointer(event, row)}
          on:mouseleave={() => (pointer = null)}
        >
          <div class="row-top">
            <span class="label" title={labelName(row[labelKey])}>{compactLabel(row[labelKey], 62)}</span>
            <span class="value">{formatValue(row[valueKey])}</span>
          </div>
          <div class="track">
            <div class="fill" style={`width: ${barWidth(row[valueKey], maxValue, 3)}`}></div>
          </div>
        </div>
      {/each}
    </div>

    <aside class="detail">
      <span>{detailTitle}</span>
      <strong>{selected ? formatValue(selected[valueKey]) : '—'}</strong>
      <h4>{selected ? labelName(selected[labelKey]) : 'No selection'}</h4>
      <p>{detailText(selected)}</p>
    </aside>
  </div>
</section>

{#if pointer}
  <div class="tooltip" style={`left: ${pointer.x}px; top: ${pointer.y}px;`}>
    <strong>{pointer.title}</strong>
    <p>{pointer.text}</p>
  </div>
{/if}

<style>
  .chart-card {
    min-height: 430px;
    border: 1px solid rgba(247, 243, 232, 0.14);
    border-radius: 28px;
    padding: 22px;
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.052), rgba(255, 255, 255, 0.016));
  }

  header {
    display: flex;
    justify-content: space-between;
    gap: 18px;
    align-items: flex-start;
    margin-bottom: 18px;
  }

  h3 {
    margin: 0 0 8px;
    color: #f7f3e8;
    font-size: 25px;
    line-height: 1.05;
    letter-spacing: -0.035em;
  }

  header p {
    max-width: 760px;
    margin: 0;
    color: #9d958b;
    font-size: 14px;
    line-height: 1.44;
  }

  .micro {
    flex: 0 0 auto;
    color: #6f685f;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
  }

  .chart-body {
    display: grid;
    grid-template-columns: minmax(0, 1fr) 230px;
    gap: 16px;
    align-items: start;
  }

  .rows {
    display: grid;
    gap: 8px;
  }

  .row {
    border: 1px solid rgba(247, 243, 232, 0.1);
    border-radius: 16px;
    padding: 11px 12px;
    background: #090908;
    cursor: pointer;
    transition: border-color 0.18s ease, background 0.18s ease, transform 0.18s ease;
  }

  .row:hover,
  .row.active {
    border-color: rgba(215, 255, 111, 0.46);
    background: rgba(215, 255, 111, 0.055);
  }

  .row:hover {
    transform: translateY(-1px);
  }

  .row-top {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    align-items: flex-start;
  }

  .label {
    max-width: 78%;
    color: #d8d0c3;
    font-size: 12.5px;
    line-height: 1.25;
  }

  .value {
    color: #d7ff6f;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
    white-space: nowrap;
  }

  .track {
    height: 8px;
    margin-top: 8px;
    border-radius: 999px;
    overflow: hidden;
    background: rgba(247, 243, 232, 0.08);
  }

  .fill {
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, #d7ff6f, rgba(215, 255, 111, 0.35));
  }

  .detail {
    min-height: 210px;
    border: 1px solid rgba(247, 243, 232, 0.14);
    border-radius: 22px;
    padding: 16px;
    background: rgba(0, 0, 0, 0.24);
  }

  .detail span {
    color: #d7ff6f;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.12em;
  }

  .detail strong {
    display: block;
    margin: 14px 0 8px;
    color: #f7f3e8;
    font-size: 38px;
    line-height: 0.95;
    letter-spacing: -0.04em;
  }

  .detail h4 {
    margin: 0 0 8px;
    color: #f7f3e8;
    font-size: 16px;
    line-height: 1.1;
  }

  .detail p {
    margin: 0;
    color: #9d958b;
    font-size: 13px;
    line-height: 1.42;
  }

  .tooltip {
    position: fixed;
    z-index: 50;
    max-width: 280px;
    border: 1px solid rgba(247, 243, 232, 0.26);
    border-radius: 14px;
    padding: 12px;
    background: #111;
    color: #d8d0c3;
    font-size: 12px;
    line-height: 1.35;
    pointer-events: none;
    transform: translate(-50%, -120%);
    box-shadow: 0 18px 50px rgba(0, 0, 0, 0.45);
  }

  .tooltip strong {
    display: block;
    margin-bottom: 4px;
    color: #f7f3e8;
    font-size: 13px;
  }

  .tooltip p {
    margin: 0;
  }

  @media (max-width: 1160px) {
    .chart-body {
      grid-template-columns: 1fr;
    }
  }

  @media (max-width: 720px) {
    header {
      display: block;
    }

    .micro {
      display: block;
      margin-top: 12px;
    }

    .row-top {
      display: grid;
    }

    .label {
      max-width: 100%;
    }
  }
</style>
