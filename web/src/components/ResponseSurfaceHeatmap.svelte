<script>
  import ChartFrame from './ChartFrame.svelte';
  import { formatFeatureName, formatModelName, formatNumber } from '../lib/presentation.js';

  export let surface = null;

  const colors = ['#162535', '#25506b', '#3e7fa0', '#6cb2c8', '#bfe56d', '#f5d46a'];

  $: zValues = (surface?.z ?? []).flat().filter((value) => Number.isFinite(Number(value))).map(Number);
  $: minZ = zValues.length ? Math.min(...zValues) : 0;
  $: maxZ = zValues.length ? Math.max(...zValues) : 1;

  function colorFor(value) {
    const number = Number(value);
    if (!Number.isFinite(number)) return 'rgba(255,255,255,.04)';
    if (maxZ === minZ) return colors[colors.length - 1];
    const ratio = (number - minZ) / (maxZ - minZ);
    const index = Math.max(0, Math.min(colors.length - 1, Math.floor(ratio * colors.length)));
    return colors[index];
  }
</script>

<ChartFrame
  title={`${formatModelName(surface?.model)} response surface`}
  description={`${formatFeatureName(surface?.feature_x)} against ${formatFeatureName(surface?.feature_y)}`}
  whyItMatters="This heatmap shows how predicted life expectancy changes when two strong signals move together while the remaining profile stays fixed."
>
  <div class="meta">
    <span>Reference region: {surface?.reference_region ?? '-'}</span>
    <span>Predicted range: {formatNumber(minZ, 1)} to {formatNumber(maxZ, 1)} years</span>
  </div>

  <div class="heatmap">
    {#each surface?.z ?? [] as row}
      <div class="row">
        {#each row as cell}
          <span class="cell" style={`background:${colorFor(cell)}`}></span>
        {/each}
      </div>
    {/each}
  </div>

  <div class="axis">
    <span>{formatFeatureName(surface?.feature_x)}</span>
    <span>{formatFeatureName(surface?.feature_y)}</span>
  </div>
</ChartFrame>

<style>
  .meta,
  .axis {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    flex-wrap: wrap;
    margin-bottom: 12px;
    color: #9fa9ad;
    font-size: 12px;
  }

  .axis {
    margin-top: 12px;
    margin-bottom: 0;
    color: #d7cfbf;
  }

  .heatmap {
    display: grid;
    gap: 2px;
    padding: 8px;
    border-radius: 18px;
    background: rgba(0, 0, 0, 0.16);
  }

  .row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(10px, 1fr));
    gap: 2px;
  }

  .cell {
    display: block;
    aspect-ratio: 1 / 1;
    border-radius: 2px;
  }
</style>
