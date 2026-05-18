export function formatNumber(value, digits = 2) {
  const number = Number(value);
  if (!Number.isFinite(number)) return '—';
  return number.toLocaleString('en-US', { maximumFractionDigits: digits });
}

export function formatPercent(value) {
  const number = Number(value);
  if (!Number.isFinite(number)) return '—';
  return `${Math.round(number * 100)}%`;
}

export function labelName(value) {
  return String(value ?? '')
    .replaceAll('_', ' ')
    .replace(/\b\w/g, (character) => character.toUpperCase());
}

export function compactLabel(value, max = 58) {
  const label = labelName(value);
  if (label.length <= max) return label;
  return `${label.slice(0, max - 1).trim()}…`;
}

export async function loadJson(name) {
  const response = await fetch(`/data/${name}.json`, { cache: 'no-store' });
  if (!response.ok) {
    throw new Error(`Could not load /data/${name}.json (${response.status})`);
  }
  return response.json();
}
