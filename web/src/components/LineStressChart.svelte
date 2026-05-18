<script>
  import { scaleLinear, valueExtent } from '../lib/chartScales.js';
  import { formatNumber } from '../lib/format.js';

  export let data = [];

  let pointer = null;

  const width = 600;
  const height = 320;
  const margin = { top: 28, right: 28, bottom: 42, left: 52 };

  $: rows = data ?? [];
  $: xExtent = rows.length ? valueExtent(rows, (row) => row.year) : [0, 1];
  $: yExtent = rows.length ? [0, Math.max(...rows.map((row) => Number(row.mean_abs_error) || 0)) * 1.18] : [0, 1];
  $: x = scaleLinear(xExtent[0], xExtent[1], margin.left, width - margin.right);
  $: y = scaleLinear(yExtent[0], yExtent[1], height - margin.bottom, margin.top);
  $: points = rows.map((row) => `${x(row.year)},${y(row.mean_abs_error)}`).join(' ');
  $: xTicks = [...new Set(rows.map((row) => Number(row.year)))].filter((_, index) => index % 2 === 0);
  $: yTicks = [0, yExtent[1] / 2, yExtent[1]];

  function showPointer(event, row) {
    pointer = {
      x: event.clientX,
      y: event.clientY,
      year: row.year,
      error: row.mean_abs_error,
      countries: row.countries
    };
  }
</script>

<div class="chart-wrap">
  <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Mean absolute prediction error by year">
    <rect x="0" y="0" width={width} height={height} fill="rgba(255,255,255,.012)" rx="18" />

    {#each yTicks as tick}
      <line x1={margin.left} y1={y(tick)} x2={width - margin.right} y2={y(tick)} stroke="rgba(247,243,232,.08)" />
      <text x={margin.left - 8} y={y(tick) + 4} fill="#9d958b" font-size="10" text-anchor="end">{formatNumber(tick, 2)}</text>
    {/each}

    <line x1={margin.left} y1={height - margin.bottom} x2={width - margin.right} y2={height - margin.bottom} stroke="rgba(247,243,232,.18)" />
    <line x1={margin.left} y1={margin.top} x2={margin.left} y2={height - margin.bottom} stroke="rgba(247,243,232,.18)" />

    {#each xTicks as tick}
      <text x={x(tick)} y={height - 14} fill="#9d958b" font-size="10" text-anchor="middle">{tick}</text>
    {/each}

    <polyline points={points} fill="none" stroke="#d7ff6f" stroke-width="2.6" />

    {#each rows as row}
      <g
        class="point"
        role="button"
        tabindex="0"
        on:mousemove={(event) => showPointer(event, row)}
        on:mouseleave={() => (pointer = null)}
      >
        <circle cx={x(row.year)} cy={y(row.mean_abs_error)} r="13" fill="rgba(215,255,111,.08)" />
        <circle cx={x(row.year)} cy={y(row.mean_abs_error)} r="4.8" fill="#f7f3e8" />
      </g>
    {/each}
  </svg>
</div>

{#if pointer}
  <div class="tooltip" style={`left: ${pointer.x}px; top: ${pointer.y}px;`}>
    <strong>{pointer.year}</strong>
    <p>Mean error: {formatNumber(pointer.error, 2)} years<br />Countries: {formatNumber(pointer.countries, 0)}</p>
  </div>
{/if}

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

  .point {
    cursor: pointer;
  }

  .point:hover circle:first-child {
    fill: rgba(215, 255, 111, 0.18);
  }

  .tooltip {
    position: fixed;
    z-index: 50;
    max-width: 260px;
    border: 1px solid rgba(247, 243, 232, 0.26);
    border-radius: 14px;
    padding: 12px;
    background: #111;
    color: #d8d0c3;
    font-size: 12px;
    line-height: 1.35;
    pointer-events: none;
    transform: translate(-50%, -120%);
  }

  .tooltip strong {
    display: block;
    margin-bottom: 4px;
    color: #f7f3e8;
  }

  .tooltip p {
    margin: 0;
  }
</style>
