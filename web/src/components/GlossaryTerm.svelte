<script>
  import { getGlossaryTerm } from '../lib/glossary.js';

  export let term = '';
  export let label = '';

  let root;
  let pinned = false;
  let hovered = false;
  let focused = false;

  $: definition = getGlossaryTerm(term);
  $: displayLabel = label || definition.label || term;
  $: isOpen = pinned || hovered || focused;

  function togglePinned() {
    pinned = !pinned;
  }

  function close() {
    pinned = false;
    hovered = false;
    focused = false;
  }

  function handleWindowClick(event) {
    if (!root || root.contains(event.target)) return;
    close();
  }

  function handleWindowKeydown(event) {
    if (event.key === 'Escape') {
      close();
    }
  }

  function handleKeydown(event) {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      togglePinned();
    }
  }
</script>

<svelte:window on:click={handleWindowClick} on:keydown={handleWindowKeydown} />

<span class="glossary" bind:this={root}>
  <button
    type="button"
    class:active={isOpen}
    class="term"
    aria-expanded={isOpen}
    on:click={togglePinned}
    on:mouseenter={() => (hovered = true)}
    on:mouseleave={() => (hovered = false)}
    on:focus={() => (focused = true)}
    on:blur={() => (focused = false)}
    on:keydown={handleKeydown}
  >
    {displayLabel}
  </button>

  {#if isOpen}
    <span class="popover" role="note">
      <strong>{definition.label}</strong>
      <span>{definition.short}</span>
      <small>{definition.long}</small>
    </span>
  {/if}
</span>

<style>
  .glossary {
    position: relative;
    display: inline-flex;
    align-items: center;
  }

  .term {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    margin: 0;
    padding: 0;
    border: 0;
    border-bottom: 1px dashed rgba(215, 255, 111, 0.65);
    background: transparent;
    color: inherit;
    font: inherit;
    cursor: help;
  }

  .term.active {
    color: #d7ff6f;
    border-bottom-color: #d7ff6f;
  }

  .popover {
    position: absolute;
    left: 0;
    top: calc(100% + 10px);
    z-index: 40;
    width: min(320px, 80vw);
    border: 1px solid rgba(247, 243, 232, 0.2);
    border-radius: 16px;
    padding: 12px 14px;
    background: rgba(12, 12, 12, 0.98);
    color: #d8d0c3;
    box-shadow: 0 16px 48px rgba(0, 0, 0, 0.28);
  }

  .popover strong,
  .popover span,
  .popover small {
    display: block;
  }

  .popover strong {
    margin-bottom: 6px;
    color: #f7f3e8;
    font-size: 12px;
    letter-spacing: 0.04em;
  }

  .popover span {
    color: #f7f3e8;
    font-size: 12px;
    line-height: 1.35;
  }

  .popover small {
    margin-top: 6px;
    color: #9d958b;
    font-size: 11px;
    line-height: 1.4;
  }
</style>
