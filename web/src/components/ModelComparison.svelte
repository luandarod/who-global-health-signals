<script>
  import { barWidth } from '../lib/chartScales.js';
  import { formatNumber, labelName } from '../lib/format.js';

  export let models = [];

  let selectedIndex = 0;
  let pointer = null;

  $: rows = models ?? [];
  $: maxMae = Math.max(...rows.map((row) => Number(row.test_mae) || 0), 0.01);
  $: selected = rows[selectedIndex] ?? rows[0];

  function scoreWidth(row) {
    const mae = Number(row.test_mae) || 0;
    return barWidth(maxMae - mae + maxMae * 0.2, maxMae * 1.2, 8);
  }

  function showPointer(event, row) {
    pointer = {
      x: event.clientX,
      y: event.clientY,
      title: labelName(row.model),
      text: `MAE ${formatNumber(row.test_mae)} years · RMSE ${formatNumber(row.test_rmse)} · R² ${formatNumber(row.test_r2)}`
    };
  }
</script>

<section class="model-layout">
  <div class="rows">
    {#each rows as row, index}
      <article
        class:active={index === selectedIndex}
        class="model-row"
        on:click={() => (selectedIndex = index)}
        on:mousemove={(event) => showPointer(event, row)}
        on:mouseleave={() => (pointer = null)}
      >
        <div>
          <strong>{labelName(row.model)}</strong>
          <span>{formatNumber(row.test_rows, 0)} recent test rows</span>
        </div>
        <div>
          <div class="track"><div class="fill" style={`width: ${scoreWidth(row)}`}></div></div>
          <p>RMSE {formatNumber(row.test_rmse)} · R² {formatNumber(row.test_r2)}</p>
        </div>
        <div class="score">
          <strong>{formatNumber(row.test_mae)}</strong>
          <span>MAE years</span>
        </div>
      </article>
    {/each}
  </div>

  {#if selected}
    <aside class="selected-card">
      <span class="kicker">Selected model</span>
      <strong>{labelName(selected.model)}</strong>
      <p>
        This model reached <b>{formatNumber(selected.test_mae)}</b> years of mean absolute error on the recent test set.
        Lower MAE means closer life-expectancy predictions.
      </p>
      <dl>
        <div><dt>RMSE</dt><dd>{formatNumber(selected.test_rmse)}</dd></div>
        <div><dt>R²</dt><dd>{formatNumber(selected.test_r2)}</dd></div>
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
    grid-template-columns: minmax(0, 1fr) 250px;
    gap: 16px;
  }

  .rows {
    display: grid;
    gap: 12px;
  }

  .model-row {
    display: grid;
    grid-template-columns: 180px minmax(0, 1fr) 118px;
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

  .model-row:first-child {
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
    line-height: 1.35;
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

  .score span {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.1em;
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
