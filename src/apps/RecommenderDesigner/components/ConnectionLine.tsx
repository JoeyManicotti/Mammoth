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
  const angle = Math.atan2(dy, dx)

  // Create a curved path with better flow direction
  // Use directional control points for smoother curves
  const controlOffset = Math.min(distance * 0.5, 150)

  // Adjust control points based on direction for smoother curves
  const cp1x = from.x + Math.cos(angle) * controlOffset
  const cp1y = from.y + Math.sin(angle) * controlOffset
  const cp2x = to.x - Math.cos(angle) * controlOffset
  const cp2y = to.y - Math.sin(angle) * controlOffset

  const path = `M ${from.x} ${from.y} C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${to.x} ${to.y}`

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
      {/* Main line with enhanced visibility */}
      <path
        d={path}
        stroke="var(--accent-blue)"
        strokeWidth="3"
        fill="none"
        strokeLinecap="round"
        className="connection-path"
      />
      {/* Enhanced Arrowhead with better visibility */}
      <defs>
        <marker
          id={`arrowhead-${id}`}
          markerWidth="12"
          markerHeight="12"
          refX="11"
          refY="6"
          orient="auto"
          markerUnits="userSpaceOnUse"
        >
          <polygon
            points="0 0, 12 6, 0 12"
            fill="var(--accent-blue)"
            stroke="var(--accent-blue)"
            strokeWidth="1"
          />
        </marker>
      </defs>
      {/* Invisible path for arrowhead attachment */}
      <path
        d={path}
        stroke="transparent"
        strokeWidth="3"
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
          r="12"
          fill="var(--bg-secondary)"
          stroke="var(--border-color)"
          strokeWidth="2"
        />
        <text
          x={midX}
          y={midY}
          textAnchor="middle"
          dominantBaseline="central"
          fontSize="14"
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
