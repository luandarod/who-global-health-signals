<script>
  export let title = '';
  export let description = '';
  export let whyItMatters = '';
</script>

<section class="chart-frame">
  <header>
    <h3>{title}</h3>
    {#if description}<p class="description">{description}</p>{/if}
    {#if whyItMatters}<p class="why">{whyItMatters}</p>{/if}
  </header>
  <div class="content">
    <slot />
  </div>
</section>

<style>
  .chart-frame {
    border: 1px solid rgba(247, 243, 232, 0.14);
    border-radius: 24px;
    padding: 20px;
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0.015));
  }

  header {
    margin-bottom: 16px;
  }

  h3 {
    margin: 0;
    color: #f7f3e8;
    font-size: 26px;
    line-height: 1.05;
    letter-spacing: -0.035em;
  }

  .description,
  .why {
    margin: 10px 0 0;
    color: #9fa9ad;
    font-size: 14px;
    line-height: 1.45;
  }

  .why {
    color: #d7cfbf;
  }
</style>
