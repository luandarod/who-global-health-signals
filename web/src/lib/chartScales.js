export function valueExtent(data, accessor) {
  const values = data.map(accessor).map(Number).filter(Number.isFinite);
  if (!values.length) return [0, 1];
  return [Math.min(...values), Math.max(...values)];
}

export function normalize(value, min, max) {
  const number = Number(value);
  if (!Number.isFinite(number)) return 0;
  if (max === min) return 1;
  return (number - min) / (max - min);
}

export function barWidth(value, max, minWidth = 4) {
  const number = Number(value);
  const maximum = Number(max);
  if (!Number.isFinite(number) || !Number.isFinite(maximum) || maximum <= 0) return `${minWidth}%`;
  return `${Math.max(minWidth, (number / maximum) * 100)}%`;
}

export function scaleLinear(domainStart, domainEnd, rangeStart, rangeEnd) {
  return (value) => {
    const number = Number(value);
    if (!Number.isFinite(number) || domainEnd === domainStart) return rangeStart;
    const ratio = (number - domainStart) / (domainEnd - domainStart);
    return rangeStart + ratio * (rangeEnd - rangeStart);
  };
}
