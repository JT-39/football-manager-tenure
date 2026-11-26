import { useRef } from 'react'
import * as d3 from 'd3'
import { useDimensions } from '@/hooks/use-dimensions'

export type BarDatum = { name: string; value: number }

type BarplotProps = {
  width: number
  height: number
  data: BarDatum[]
}

// Space around the bars for the axis labels. Bars are drawn inside this box.
const MARGIN = { top: 20, right: 20, bottom: 70, left: 50 }

/**
 * The responsive version: it measures its box and passes the size down.
 * It does nothing else, so you can give it any chart props without changing it.
 */
export function ResponsiveBarplot(props: Omit<BarplotProps, 'width' | 'height'>) {
  const chartRef = useRef<HTMLDivElement>(null)
  const size = useDimensions(chartRef)

  return (
    <div ref={chartRef} style={{ width: '100%', height: '100%' }}>
      <Barplot width={size.width} height={size.height} {...props} />
    </div>
  )
}

/**
 * A text version of the chart for screen readers, e.g. "Bar chart: Alpha 42, Beta 28".
 * Sighted users see the bars; this gives everyone the same numbers.
 */
function describe(data: BarDatum[]): string {
  const values = data.map((d) => `${d.name} ${d.value}`).join(', ')
  return `Bar chart: ${values}`
}

/**
 * The chart itself. D3 works out the positions (the maths); React draws the
 * elements with JSX (the rendering). It never touches the page directly.
 */
function Barplot({ width, height, data }: BarplotProps) {
  // Before the size is known there is nothing to draw.
  if (width === 0 || height === 0) return null

  const boundsWidth = width - MARGIN.left - MARGIN.right
  const boundsHeight = height - MARGIN.top - MARGIN.bottom

  // Horizontal: one band per bar. Vertical: value to pixel height, upside down
  // because SVG's y axis points down the page.
  const xScale = d3
    .scaleBand()
    .domain(data.map((d) => d.name))
    .range([0, boundsWidth])
    .padding(0.2)

  const yScale = d3
    .scaleLinear()
    .domain([0, d3.max(data, (d) => d.value) ?? 0])
    .range([boundsHeight, 0])
    .nice()

  // More ticks on taller charts, fewer on short ones (one tick per ~60px).
  const yTicks = yScale.ticks(Math.max(2, Math.floor(boundsHeight / 60)))

  return (
    <svg width={width} height={height} role="img" aria-label={describe(data)}>
      <g transform={`translate(${MARGIN.left}, ${MARGIN.top})`}>
        {/* Horizontal grid lines and their labels */}
        {yTicks.map((tick) => (
          <g key={tick} transform={`translate(0, ${yScale(tick)})`}>
            <line x1={0} x2={boundsWidth} stroke="currentColor" strokeOpacity={0.1} />
            <text x={-8} dy="0.32em" textAnchor="end" fontSize={12} fill="currentColor">
              {tick}
            </text>
          </g>
        ))}

        {/* One bar per row. The key is the bar's name, so React can track each bar. */}
        {data.map((d) => (
          <g key={d.name}>
            <rect
              x={xScale(d.name)}
              y={yScale(d.value)}
              width={xScale.bandwidth()}
              height={boundsHeight - yScale(d.value)}
              fill="var(--chart-1)"
            />
            <text
              transform={`translate(${(xScale(d.name) ?? 0) + xScale.bandwidth() / 2}, ${boundsHeight + 12}) rotate(-35)`}
              textAnchor="end"
              fontSize={12}
              fill="currentColor"
            >
              {d.name}
            </text>
          </g>
        ))}
      </g>
    </svg>
  )
}
