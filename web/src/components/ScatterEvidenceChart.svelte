<script>
  import ChartFrame from './ChartFrame.svelte';
  import { scaleLinear, valueExtent } from '../lib/chartScales.js';
  import { formatNumber } from '../lib/presentation.js';

  export let title = '';
  export let description = '';
  export let whyItMatters = '';
  export let data = [];

  const width = 520;
  const height = 360;
  const margin = { top: 24, right: 24, bottom: 44, left: 48 };

  $: rows = data ?? [];
  $: xExtent = rows.length ? valueExtent(rows, (row) => row.actual) : [0, 1];
  $: yExtent = rows.length ? valueExtent(rows, (row) => row.predicted) : [0, 1];
  $: low = Math.min(xExtent[0], yExtent[0]);
  $: high = Math.max(xExtent[1], yExtent[1]);
  $: x = scaleLinear(low, high, margin.left, width - margin.right);
  $: y = scaleLinear(low, high, height - margin.bottom, margin.top);
  $: ticks = [low, (low + high) / 2, high];
</script>

<ChartFrame {title} {description} {whyItMatters}>
  <div class="chart-wrap">
    <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label={title}>
      <rect x="0" y="0" width={width} height={height} fill="rgba(255,255,255,.012)" rx="18" />

      {#each ticks as tick}
        <line x1={margin.left} y1={y(tick)} x2={width - margin.right} y2={y(tick)} stroke="rgba(247,243,232,.08)" />
        <line x1={x(tick)} y1={margin.top} x2={x(tick)} y2={height - margin.bottom} stroke="rgba(247,243,232,.08)" />
        <text x={x(tick)} y={height - 14} fill="#9fa9ad" font-size="10" text-anchor="middle">{formatNumber(tick, 0)}</text>
        <text x={margin.left - 8} y={y(tick) + 4} fill="#9fa9ad" font-size="10" text-anchor="end">{formatNumber(tick, 0)}</text>
      {/each}

      <line x1={margin.left} y1={height - margin.bottom} x2={width - margin.right} y2={height - margin.bottom} stroke="rgba(247,243,232,.16)" />
      <line x1={margin.left} y1={margin.top} x2={margin.left} y2={height - margin.bottom} stroke="rgba(247,243,232,.16)" />
      <line x1={x(low)} y1={y(low)} x2={x(high)} y2={y(high)} stroke="rgba(217,255,121,.55)" stroke-dasharray="5 5" />

      {#each rows as row}
        <circle cx={x(row.actual)} cy={y(row.predicted)} r="3.2" fill="rgba(144,215,255,.72)" />
      {/each}

      <text x={width / 2} y={height - 4} fill="#9fa9ad" font-size="11" text-anchor="middle">Observed life expectancy</text>
      <text transform={`translate(16 ${height / 2}) rotate(-90)`} fill="#9fa9ad" font-size="11" text-anchor="middle">Predicted life expectancy</text>
    </svg>
  </div>
</ChartFrame>

<style>
  .chart-wrap {
    width: 100%;
    border-radius: 22px;
    background: rgba(0, 0, 0, 0.14);
    overflow: hidden;
  }

  svg {
    width: 100%;
    height: auto;
    display: block;
  }
</style>
