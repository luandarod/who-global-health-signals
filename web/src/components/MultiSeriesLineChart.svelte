<script>
  import ChartFrame from './ChartFrame.svelte';
  import { scaleLinear, valueExtent } from '../lib/chartScales.js';
  import { formatNumber, labelName } from '../lib/presentation.js';

  export let title = '';
  export let description = '';
  export let whyItMatters = '';
  export let data = [];
  export let xKey = 'year';
  export let yKey = 'value';
  export let seriesKey = 'series';
  export let yLabel = '';
  export let colorMap = {};
  export let filterFn = null;

  const width = 720;
  const height = 340;
  const margin = { top: 24, right: 22, bottom: 42, left: 54 };

  $: rows = typeof filterFn === 'function' ? (data ?? []).filter(filterFn) : (data ?? []);
  $: seriesNames = [...new Set(rows.map((row) => row?.[seriesKey] ?? 'Series'))];
  $: grouped = seriesNames.map((name) => ({
    name,
    color: colorMap[name] ?? '#d9ff79',
    rows: rows.filter((row) => (row?.[seriesKey] ?? 'Series') === name).sort((a, b) => Number(a?.[xKey]) - Number(b?.[xKey]))
  }));
  $: xExtent = rows.length ? valueExtent(rows, (row) => row[xKey]) : [0, 1];
  $: yExtent = rows.length ? [0, Math.max(...rows.map((row) => Number(row?.[yKey]) || 0)) * 1.12] : [0, 1];
  $: x = scaleLinear(xExtent[0], xExtent[1], margin.left, width - margin.right);
  $: y = scaleLinear(yExtent[0], yExtent[1], height - margin.bottom, margin.top);
  $: yTicks = [0, yExtent[1] / 2, yExtent[1]];
  $: xTicks = [...new Set(rows.map((row) => Number(row?.[xKey])))].filter((_, index) => index % 2 === 0);
</script>

<ChartFrame {title} {description} {whyItMatters}>
  <div class="legend">
    {#each grouped as series}
      <span><i style={`background:${series.color}`}></i>{labelName(series.name)}</span>
    {/each}
  </div>

  <div class="chart-wrap">
    <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label={title}>
      <rect x="0" y="0" width={width} height={height} fill="rgba(255,255,255,.012)" rx="18" />

      {#each yTicks as tick}
        <line x1={margin.left} y1={y(tick)} x2={width - margin.right} y2={y(tick)} stroke="rgba(247,243,232,.08)" />
        <text x={margin.left - 8} y={y(tick) + 4} fill="#9fa9ad" font-size="10" text-anchor="end">{formatNumber(tick, 2)}</text>
      {/each}

      <line x1={margin.left} y1={height - margin.bottom} x2={width - margin.right} y2={height - margin.bottom} stroke="rgba(247,243,232,.16)" />
      <line x1={margin.left} y1={margin.top} x2={margin.left} y2={height - margin.bottom} stroke="rgba(247,243,232,.16)" />

      {#each xTicks as tick}
        <text x={x(tick)} y={height - 14} fill="#9fa9ad" font-size="10" text-anchor="middle">{tick}</text>
      {/each}

      {#each grouped as series}
        <polyline
          points={series.rows.map((row) => `${x(row[xKey])},${y(row[yKey])}`).join(' ')}
          fill="none"
          stroke={series.color}
          stroke-width="2.4"
        />
      {/each}

      {#if yLabel}
        <text transform={`translate(16 ${height / 2}) rotate(-90)`} fill="#9fa9ad" font-size="11" text-anchor="middle">{yLabel}</text>
      {/if}
    </svg>
  </div>
</ChartFrame>

<style>
  .legend {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-bottom: 12px;
  }

  .legend span {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    color: #d7cfbf;
    font-size: 12px;
  }

  .legend i {
    width: 10px;
    height: 10px;
    border-radius: 999px;
    display: inline-block;
  }

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
