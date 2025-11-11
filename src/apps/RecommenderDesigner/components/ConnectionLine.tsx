import { Position } from '../types'
import './ConnectionLine.css'

interface ConnectionLineProps {
  id: string
  from: Position
  to: Position
  onRemove: () => void
}

const ConnectionLine = ({ id, from, to, onRemove }: ConnectionLineProps) => {
  // Calculate control points for a smooth curve
  const dx = to.x - from.x
  const dy = to.y - from.y
  const distance = Math.sqrt(dx * dx + dy * dy)

  // Create a curved path
  const controlOffset = Math.min(distance * 0.5, 100)
  const path = `M ${from.x} ${from.y} C ${from.x + controlOffset} ${from.y}, ${to.x - controlOffset} ${to.y}, ${to.x} ${to.y}`

  // Calculate midpoint for the delete button
  const midX = (from.x + to.x) / 2
  const midY = (from.y + to.y) / 2

  return (
    <g className="connection-line">
      {/* Shadow/outline */}
      <path
        d={path}
        stroke="var(--bg-primary)"
        strokeWidth="6"
        fill="none"
        strokeLinecap="round"
      />
      {/* Main line */}
      <path
        d={path}
        stroke="var(--accent-blue)"
        strokeWidth="2"
        fill="none"
        strokeLinecap="round"
        className="connection-path"
      />
      {/* Arrowhead */}
      <defs>
        <marker
          id={`arrowhead-${id}`}
          markerWidth="10"
          markerHeight="10"
          refX="9"
          refY="3"
          orient="auto"
        >
          <polygon
            points="0 0, 10 3, 0 6"
            fill="var(--accent-blue)"
          />
        </marker>
      </defs>
      <path
        d={path}
        stroke="var(--accent-blue)"
        strokeWidth="2"
        fill="none"
        markerEnd={`url(#arrowhead-${id})`}
      />
      {/* Delete button */}
      <g
        className="connection-delete"
        onClick={onRemove}
        style={{ cursor: 'pointer' }}
      >
        <circle
          cx={midX}
          cy={midY}
          r="10"
          fill="var(--bg-secondary)"
          stroke="var(--border-color)"
          strokeWidth="1"
        />
        <text
          x={midX}
          y={midY}
          textAnchor="middle"
          dominantBaseline="central"
          fontSize="12"
          fill="var(--accent-error)"
          fontWeight="bold"
        >
          ×
        </text>
      </g>
    </g>
  )
}

export default ConnectionLine
