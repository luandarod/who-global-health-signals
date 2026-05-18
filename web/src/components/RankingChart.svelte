<script>
  import ChartFrame from './ChartFrame.svelte';
  import { barWidth } from '../lib/chartScales.js';
  import { compactLabel, formatNumber, formatPercent, formatModelName, labelName } from '../lib/presentation.js';

  export let title = '';
  export let description = '';
  export let whyItMatters = '';
  export let data = [];
  export let labelKey = 'label';
  export let valueKey = 'value';
  export let mode = 'number';
  export let limit = 10;
  export let highlightFirst = false;
  export let modelLabels = false;

  $: rows = (data ?? []).slice(0, limit);
  $: maxValue = Math.max(...rows.map((row) => Number(row[valueKey]) || 0), 0.01);

  function labelFor(row) {
    const raw = row?.[labelKey];
    return modelLabels ? formatModelName(raw) : labelName(raw);
  }

  function formatValue(value) {
    return mode === 'percent' ? formatPercent(value, 0) : formatNumber(value, 3);
  }
</script>

<ChartFrame {title} {description} {whyItMatters}>
  <div class="rows">
    {#each rows as row, index}
      <div class:top={highlightFirst && index === 0} class="row">
        <div class="row-top">
          <span class="label" title={labelFor(row)}>{compactLabel(labelFor(row), 40)}</span>
          <span class="value">{formatValue(row[valueKey])}</span>
        </div>
        <div class="track">
          <div class="fill" style={`width: ${barWidth(row[valueKey], maxValue, 3)}`}></div>
        </div>
      </div>
    {/each}
  </div>
</ChartFrame>

<style>
  .rows {
    display: grid;
    gap: 8px;
  }

  .row {
    border: 1px solid rgba(247, 243, 232, 0.1);
    border-radius: 16px;
    padding: 11px 12px;
    background: rgba(0, 0, 0, 0.18);
  }

  .row.top {
    border-color: rgba(217, 255, 121, 0.45);
    background: rgba(217, 255, 121, 0.06);
  }

  .row-top {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    align-items: flex-start;
  }

  .label {
    max-width: 78%;
    color: #d7cfbf;
    font-size: 13px;
    line-height: 1.25;
  }

  .value {
    color: #d9ff79;
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
    background: linear-gradient(90deg, #d9ff79, rgba(144, 215, 255, 0.65));
  }
</style>
