interface DeltaChartProps {
  distances: number[];
  deltas: number[];
}

const WIDTH = 720;
const HEIGHT = 220;
const PAD_X = 44;
const PAD_Y = 24;

function range(values: number[]): [number, number] {
  if (values.length === 0) {
    return [0, 1];
  }

  let min = values[0] ?? 0;
  let max = values[0] ?? 0;

  for (const value of values) {
    min = Math.min(min, value);
    max = Math.max(max, value);
  }

  if (min === max) {
    const padding = Math.max(Math.abs(min) * 0.1, 0.001);
    return [min - padding, max + padding];
  }

  return [min, max];
}

function scale(value: number, min: number, max: number, start: number, end: number): number {
  return start + ((value - min) / (max - min)) * (end - start);
}

export function DeltaChart({ distances, deltas }: DeltaChartProps) {
  const count = Math.min(distances.length, deltas.length);
  const xValues = distances.slice(0, count);
  const yValues = deltas.slice(0, count);

  const [xMin, xMax] = range(xValues);
  const [rawYMin, rawYMax] = range(yValues);
  const yMin = Math.min(rawYMin, 0);
  const yMax = Math.max(rawYMax, 0);

  const points = xValues
    .map((distance, index) => {
      const delta = yValues[index] ?? 0;
      const x = scale(distance, xMin, xMax, PAD_X, WIDTH - PAD_X);
      const y = scale(delta, yMin, yMax, HEIGHT - PAD_Y, PAD_Y);
      return `${x.toFixed(2)},${y.toFixed(2)}`;
    })
    .join(" ");

  const zeroY = scale(0, yMin, yMax, HEIGHT - PAD_Y, PAD_Y);
  const deltaMin = yValues.length === 0 ? 0 : Math.min(...yValues);
  const deltaMax = yValues.length === 0 ? 0 : Math.max(...yValues);
  const descriptionId = "delta-chart-description";

  return (
    <div className="delta-chart">
      <svg
        role="img"
        aria-label="Delta time over distance"
        aria-describedby={descriptionId}
        viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
        data-point-count={String(count)}
      >
        <title>Delta time over distance</title>
        <line
          className="delta-chart__zero"
          x1={PAD_X}
          x2={WIDTH - PAD_X}
          y1={zeroY}
          y2={zeroY}
        />
        <polyline className="delta-chart__line" points={points} fill="none" />
        <text x={PAD_X} y={HEIGHT - 4}>
          {xMin.toFixed(0)} m
        </text>
        <text x={WIDTH - PAD_X} y={HEIGHT - 4} textAnchor="end">
          {xMax.toFixed(0)} m
        </text>
        <text x={4} y={PAD_Y + 4}>
          {yMax.toFixed(3)} s
        </text>
        <text x={4} y={HEIGHT - PAD_Y}>
          {yMin.toFixed(3)} s
        </text>
      </svg>
      <p id={descriptionId} className="visually-hidden">
        Delta B minus A ranges from {deltaMin.toFixed(3)} to {deltaMax.toFixed(3)} seconds
        across {count} distance points.
      </p>
    </div>
  );
}
