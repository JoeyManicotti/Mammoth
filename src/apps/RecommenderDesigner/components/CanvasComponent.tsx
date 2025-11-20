import { useDrag } from 'react-dnd'
import { ComponentData } from '../types'
import { getSimplifiedComponent, getComponentColor, isValidConnection } from '../simplifiedComponents'
import './CanvasComponent.css'

interface CanvasComponentProps {
  component: ComponentData
  isSelected: boolean
  isConnecting: boolean
  connectingFrom: string | null
  onUpdate: (id: string, updates: Partial<ComponentData>) => void
  onRemove: (id: string) => void
  onSelect: (id: string) => void
  onConnect: (from: string, to: string) => void
  onDoubleClick: (id: string) => void
  onStartConnection: (id: string | null) => void
  allComponents: ComponentData[]
}

const CanvasComponent = ({
  component,
  isSelected,
  isConnecting,
  connectingFrom,
  onUpdate,
  onRemove,
  onSelect,
  onConnect,
  onDoubleClick,
  onStartConnection,
  allComponents
}: CanvasComponentProps) => {
  const [{ isDragging }, drag] = useDrag(() => ({
    type: 'canvas-component',
    item: () => {
      return { id: component.id, startPosition: component.position }
    },
    collect: (monitor) => ({
      isDragging: monitor.isDragging()
    }),
    end: (item, monitor) => {
      const delta = monitor.getDifferenceFromInitialOffset()
      if (delta && item.startPosition) {
        onUpdate(component.id, {
          position: {
            x: item.startPosition.x + delta.x,
            y: item.startPosition.y + delta.y
          }
        })
      }
    }
  }), [component.id, component.position, onUpdate])

  const handleClick = (e: React.MouseEvent) => {
    e.stopPropagation()
    onSelect(component.id)
  }

  const handleDoubleClick = (e: React.MouseEvent) => {
    e.stopPropagation()
    onDoubleClick(component.id)
  }

  const handleConnectionPointClick = (e: React.MouseEvent) => {
    e.stopPropagation()

    if (!connectingFrom) {
      // Start connection from this component
      onStartConnection(component.id)
    } else if (connectingFrom === component.id) {
      // Cancel connection if clicking same component
      onStartConnection(null)
    } else {
      // Complete connection to this component
      const fromComp = allComponents.find(c => c.id === connectingFrom)
      if (fromComp && isValidConnection(fromComp.type, component.type)) {
        onConnect(connectingFrom, component.id)
        onStartConnection(null)
      } else {
        // Invalid connection - show feedback or just cancel
        onStartConnection(null)
      }
    }
  }

  const handleContextMenu = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()

    // Right-click auto-connect: start connection if not currently connecting
    if (!connectingFrom) {
      onStartConnection(component.id)
    } else if (connectingFrom !== component.id) {
      // Complete connection if already connecting from another component
      const fromComp = allComponents.find(c => c.id === connectingFrom)
      if (fromComp && isValidConnection(fromComp.type, component.type)) {
        onConnect(connectingFrom, component.id)
        onStartConnection(null)
      } else {
        onStartConnection(null)
      }
    } else {
      // Cancel connection if right-clicking the same component
      onStartConnection(null)
    }
  }

  const handleDeleteButtonClick = (e: React.MouseEvent) => {
    e.stopPropagation()
    e.preventDefault()
    onRemove(component.id)
  }

  const getIcon = () => {
    // Try to get icon from simplified components first
    const simplifiedComp = getSimplifiedComponent(component.type)
    if (simplifiedComp) {
      return simplifiedComp.icon
    }

    // Fallback to old icon map
    const iconMap: Record<string, string> = {
      'data-source': '📊',
      'user-profile': '👤',
      'item-catalog': '📦',
      'feature-extraction': '🔍',
      'collaborative-filter': '🤝',
      'content-filter': '📝',
      'matrix-factorization': '🔢',
      'deep-learning': '🧠',
      'ranking': '📈',
      'output': '📤',
      'evaluation': '✅'
    }
    return iconMap[component.type] || '📦'
  }

  // Get color for component based on category
  const simplifiedComp = getSimplifiedComponent(component.type)
  const colors = simplifiedComp ? getComponentColor(simplifiedComp.category) : undefined

  return (
    <div
      ref={drag}
      className={`canvas-component ${simplifiedComp ? `canvas-component-${simplifiedComp.category}` : ''} ${isSelected ? 'selected' : ''} ${isDragging ? 'dragging' : ''} ${isConnecting ? 'connecting' : ''}`}
      style={{
        left: component.position.x,
        top: component.position.y,
        ...(colors ? {
          background: colors.gradient,
          borderColor: colors.border
        } : {})
      }}
      onClick={handleClick}
      onDoubleClick={handleDoubleClick}
      onContextMenu={handleContextMenu}
    >
      {/* Delete button (visible when selected) */}
      {isSelected && (
        <button
          className="component-delete-button"
          onClick={handleDeleteButtonClick}
          title="Delete component"
        >
          ×
        </button>
      )}

      <div className="component-icon">{getIcon()}</div>
      <div
        className="component-label"
        style={colors ? { color: colors.text } : {}}
      >{component.label}</div>

      {/* Connection points - Blue dots on each edge */}
      <div
        className={`connection-point top ${connectingFrom === component.id ? 'active' : ''}`}
        onClick={handleConnectionPointClick}
        title="Click to connect"
      />
      <div
        className={`connection-point right ${connectingFrom === component.id ? 'active' : ''}`}
        onClick={handleConnectionPointClick}
        title="Click to connect"
      />
      <div
        className={`connection-point bottom ${connectingFrom === component.id ? 'active' : ''}`}
        onClick={handleConnectionPointClick}
        title="Click to connect"
      />
      <div
        className={`connection-point left ${connectingFrom === component.id ? 'active' : ''}`}
        onClick={handleConnectionPointClick}
        title="Click to connect"
      />
    </div>
  )
}

export default CanvasComponent
