<script>
  import GlossaryTerm from './GlossaryTerm.svelte';
  import { barWidth } from '../lib/chartScales.js';
  import { formatDependency, formatModelName, formatNumber } from '../lib/presentation.js';

  export let models = [];

  let selectedIndex = 0;
  let pointer = null;

  $: rows = models ?? [];
  $: maxMae = Math.max(...rows.map((row) => Number(row.test_mae) || 0), 0.01);
  $: selected = rows[selectedIndex] ?? rows[0];
  $: localRows = rows.filter((row) => row.dependency !== 'priorlabs_api');
  $: bestLocal = localRows[0];
  $: gapToBestLocal =
    selected && bestLocal
      ? Math.abs((Number(bestLocal.test_mae) || 0) - (Number(rows[0]?.test_mae) || 0))
      : null;

  function scoreWidth(row) {
    const mae = Number(row.test_mae) || 0;
    return barWidth(maxMae - mae + maxMae * 0.2, maxMae * 1.2, 8);
  }

  function selectRow(index) {
    selectedIndex = index;
  }

  function handleKeydown(event, index) {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      selectRow(index);
    }
  }

  function showPointer(event, row) {
    pointer = {
      x: event.clientX,
      y: event.clientY,
      title: formatModelName(row.model),
      text: `MAE ${formatNumber(row.test_mae)} | RMSE ${formatNumber(row.test_rmse)} | R2 ${formatNumber(row.test_r2)}`
    };
  }
</script>

<section class="model-layout">
  <div class="rows">
    {#each rows as row, index}
      <article
        class:active={index === selectedIndex}
        class:isTop={index === 0}
        class="model-row"
        role="button"
        tabindex="0"
        aria-pressed={index === selectedIndex}
        on:click={() => selectRow(index)}
        on:keydown={(event) => handleKeydown(event, index)}
        on:mousemove={(event) => showPointer(event, row)}
        on:mouseleave={() => (pointer = null)}
      >
        <div>
          <strong>{formatModelName(row.model)}</strong>
          <span>{formatDependency(row.dependency)} | {formatNumber(row.test_rows, 0)} recent test rows</span>
        </div>
        <div>
          <div class="track"><div class="fill" style={`width: ${scoreWidth(row)}`}></div></div>
          <p>
            <GlossaryTerm term="rmse" label="RMSE" />
            {formatNumber(row.test_rmse)}
            |
            <GlossaryTerm term="r2" label="R2" />
            {formatNumber(row.test_r2)}
          </p>
        </div>
        <div class="score">
          <strong>{formatNumber(row.test_mae)}</strong>
          <span><GlossaryTerm term="mae" label="MAE" /> years</span>
        </div>
      </article>
    {/each}
  </div>

  {#if selected}
    <aside class="selected-card">
      <span class="kicker">{selectedIndex === 0 ? 'Global champion' : 'Selected model'}</span>
      <strong>{formatModelName(selected.model)}</strong>
      <p>
        This model reached <b>{formatNumber(selected.test_mae)}</b> years of
        <GlossaryTerm term="mae" label="MAE" /> on the temporal holdout.
        Lower error means closer life-expectancy predictions.
      </p>
      {#if selectedIndex === 0 && bestLocal}
        <p>
          The final winner is the external TabPFN reference, while the best local benchmark is
          <b>{formatModelName(bestLocal.model)}</b> at {formatNumber(bestLocal.test_mae)} MAE.
          The gap between them is {formatNumber(gapToBestLocal, 2)} years.
        </p>
      {/if}
      <dl>
        <div><dt><GlossaryTerm term="rmse" label="RMSE" /></dt><dd>{formatNumber(selected.test_rmse)}</dd></div>
        <div><dt><GlossaryTerm term="r2" label="R2" /></dt><dd>{formatNumber(selected.test_r2)}</dd></div>
      </dl>
    </aside>
  {/if}
</section>

{#if pointer}
  <div class="tooltip" style={`left: ${pointer.x}px; top: ${pointer.y}px;`}>
    <strong>{pointer.title}</strong>
    <p>{pointer.text}</p>
  </div>
{/if}

<style>
  .model-layout {
    display: grid;
    grid-template-columns: minmax(0, 1fr) 270px;
    gap: 16px;
  }

  .rows {
    display: grid;
    gap: 12px;
  }

  .model-row {
    display: grid;
    grid-template-columns: 190px minmax(0, 1fr) 118px;
    gap: 16px;
    align-items: center;
    border: 1px solid rgba(247, 243, 232, 0.14);
    border-radius: 22px;
    padding: 16px;
    background: #090908;
    cursor: pointer;
    transition: border-color 0.18s ease, background 0.18s ease, transform 0.18s ease;
  }

  .model-row:hover,
  .model-row.active {
    border-color: rgba(215, 255, 111, 0.46);
    background: rgba(215, 255, 111, 0.055);
  }

  .model-row:hover {
    transform: translateY(-1px);
  }

  .model-row.isTop {
    background: linear-gradient(135deg, rgba(215, 255, 111, 0.13), rgba(255, 255, 255, 0.025));
    border-color: rgba(215, 255, 111, 0.42);
  }

  .model-row strong {
    display: block;
    color: #f7f3e8;
    font-size: 20px;
    letter-spacing: -0.03em;
  }

  .model-row span,
  .model-row p {
    color: #9d958b;
    font-size: 12px;
    line-height: 1.4;
  }

  .model-row span {
    display: block;
    margin-top: 5px;
  }

  .model-row p {
    margin: 8px 0 0;
  }

  .track {
    height: 9px;
    border-radius: 999px;
    overflow: hidden;
    background: rgba(247, 243, 232, 0.08);
  }

  .fill {
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, #d7ff6f, rgba(215, 255, 111, 0.35));
  }

  .score {
    text-align: right;
  }

  .score strong {
    color: #d7ff6f;
    font-size: 32px;
    line-height: 0.95;
    font-weight: 900;
  }

  .selected-card {
    border: 1px solid rgba(247, 243, 232, 0.14);
    border-radius: 22px;
    padding: 16px;
    background: rgba(0, 0, 0, 0.24);
  }

  .kicker {
    color: #d7ff6f;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.12em;
  }

  .selected-card > strong {
    display: block;
    margin-top: 14px;
    color: #f7f3e8;
    font-size: 26px;
    line-height: 1;
  }

  .selected-card p {
    color: #9d958b;
    font-size: 13px;
    line-height: 1.45;
  }

  dl {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    margin: 14px 0 0;
  }

  dl div {
    border-top: 1px solid rgba(247, 243, 232, 0.14);
    padding-top: 10px;
  }

  dt {
    color: #6f685f;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    text-transform: uppercase;
  }

  dd {
    margin: 4px 0 0;
    color: #f7f3e8;
    font-weight: 800;
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
  }

  .tooltip strong {
    display: block;
    margin-bottom: 4px;
    color: #f7f3e8;
  }

  .tooltip p {
    margin: 0;
  }

  @media (max-width: 1160px) {
    .model-layout,
    .model-row {
      grid-template-columns: 1fr;
    }

    .score {
      text-align: left;
    }
  }
</style>
