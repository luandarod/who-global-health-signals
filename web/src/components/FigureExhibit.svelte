<script>
  export let src = '';
  export let alt = '';
  export let eyebrow = '';
  export let title = '';
  export let note = '';
</script>

<figure class="figure-card">
  <div class="figure-head">
    {#if eyebrow}<span>{eyebrow}</span>{/if}
    {#if title}<h3>{title}</h3>{/if}
    {#if note}<p>{note}</p>{/if}
  </div>
  <img src={src} alt={alt} loading="lazy" />
</figure>

<style>
  .figure-card {
    margin: 0;
    border: 1px solid rgba(247, 243, 232, 0.14);
    border-radius: 24px;
    overflow: hidden;
    background: rgba(255, 255, 255, 0.02);
  }

  .figure-head {
    padding: 18px 18px 14px;
    border-bottom: 1px solid rgba(247, 243, 232, 0.1);
  }

  span {
    display: block;
    margin-bottom: 10px;
    color: #d7ff6f;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
  }

  h3 {
    margin: 0;
    color: #f7f3e8;
    font-size: 22px;
    line-height: 1.1;
    letter-spacing: -0.03em;
  }

  p {
    margin: 10px 0 0;
    color: #9d958b;
    font-size: 13px;
    line-height: 1.45;
  }

  img {
    display: block;
    width: 100%;
    height: auto;
    background: #fff;
  }
</style>
