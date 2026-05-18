<script>
  import GlossaryTerm from './GlossaryTerm.svelte';
  import { formatModelName, formatNumber, formatYearRange } from '../lib/presentation.js';

  export let summary = null;
  export let models = [];

  $: bestModel = summary?.best_model ?? null;
  $: localChampion = (models ?? []).find((row) => row.dependency !== 'priorlabs_api');
  $: rows = summary?.dataset ?? {};
  $: yearSpan = formatYearRange(rows.min_year, rows.max_year);
</script>

<section class="executive-case">
  <div class="copy">
    <span class="eyebrow">Executive case</span>
    <h2>Public WHO indicators explain life expectancy differences unusually well.</h2>
    <p class="lead">
      We analyzed <b>{formatNumber(rows.full_rows, 0)}</b> country-year records covering
      <b>{formatNumber(rows.countries, 0)}</b> countries and entities across <b>{yearSpan}</b>,
      then tested whether those signals could predict life expectancy on a future-facing holdout from
      <b>2015 onward</b>.
    </p>
    <p>
      The answer is yes. On the cleaned analytical panel, the final champion
      <b>{formatModelName(bestModel?.name)}</b> reached
      <b>{formatNumber(bestModel?.test_mae, 3)}</b> years of
      <GlossaryTerm term="mae" label="MAE" />, while the strongest local trainable model,
      <b>{formatModelName(localChampion?.model)}</b>, reached
      <b>{formatNumber(localChampion?.test_mae, 3)}</b>.
    </p>
    <p>
      Business reading: the WHO public indicator layer carries a strong enough
      <GlossaryTerm term="predictive_signal" label="predictive signal" /> to support benchmarking,
      comparative monitoring, and targeted follow-up on countries or periods where the model still struggles.
    </p>
  </div>

  <div class="facts">
    <article>
      <strong>{formatNumber(rows.modeling_rows, 0)}</strong>
      <span>Modeling-ready rows</span>
      <p>Records retained after the quality and completeness filters.</p>
    </article>
    <article>
      <strong>{formatNumber(bestModel?.test_rmse, 3)}</strong>
      <span>Champion RMSE</span>
      <p>Large misses remain rare even on the 2015+ holdout.</p>
    </article>
    <article>
      <strong>{formatNumber(bestModel?.test_r2, 4)}</strong>
      <span>Champion R2</span>
      <p>The observed variation in life expectancy is almost entirely captured by the model.</p>
    </article>
    <article>
      <strong>{formatNumber((localChampion?.test_mae ?? 0) - (bestModel?.test_mae ?? 0), 3)}</strong>
      <span>Gap to best local model</span>
      <p>The external reference wins, but the local benchmark remains strong and credible.</p>
    </article>
  </div>
</section>

<style>
  .executive-case {
    display: grid;
    grid-template-columns: 1.15fr 0.85fr;
    gap: 18px;
    margin: 22px 0 0;
  }

  .copy,
  .facts {
    border: 1px solid rgba(247, 243, 232, 0.14);
    border-radius: 28px;
    padding: 24px;
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.055), rgba(255, 255, 255, 0.015));
  }

  .eyebrow {
    display: block;
    color: #d9ff79;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
  }

  h2 {
    margin: 14px 0;
    color: #f4efe3;
    font-size: clamp(34px, 4vw, 58px);
    line-height: 0.98;
    letter-spacing: -0.04em;
  }

  .lead,
  .copy p {
    margin: 0 0 14px;
    color: #d7cfbf;
    font-size: 16px;
    line-height: 1.55;
  }

  .facts {
    display: grid;
    gap: 12px;
    align-content: start;
  }

  article {
    border: 1px solid rgba(247, 243, 232, 0.1);
    border-radius: 20px;
    padding: 16px;
    background: rgba(0, 0, 0, 0.18);
  }

  strong {
    display: block;
    color: #d9ff79;
    font-size: 36px;
    line-height: 0.95;
    letter-spacing: -0.04em;
  }

  article span {
    display: block;
    margin-top: 10px;
    color: #f4efe3;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }

  article p {
    margin: 10px 0 0;
    color: #9fa9ad;
    font-size: 13px;
    line-height: 1.4;
  }

  @media (max-width: 1160px) {
    .executive-case {
      grid-template-columns: 1fr;
    }
  }
</style>
