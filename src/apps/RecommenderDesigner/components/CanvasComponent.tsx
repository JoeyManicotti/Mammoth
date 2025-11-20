import { useState } from 'react'
import { useDrag } from 'react-dnd'
import { ComponentData } from '../types'
import { getSimplifiedComponent, getComponentColor } from '../simplifiedComponents'
import './CanvasComponent.css'

interface CanvasComponentProps {
  component: ComponentData
  isSelected: boolean
  onUpdate: (id: string, updates: Partial<ComponentData>) => void
  onRemove: (id: string) => void
  onSelect: (id: string) => void
  onConnect: (from: string, to: string) => void
  onDoubleClick: (id: string) => void
  allComponents: ComponentData[]
}

const CanvasComponent = ({
  component,
  isSelected,
  onUpdate,
  onRemove,
  onSelect,
  onDoubleClick,
}: CanvasComponentProps) => {
  const [showMenu, setShowMenu] = useState(false)

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

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation()
    onRemove(component.id)
    setShowMenu(false)
  }

  const handleConfigure = (e: React.MouseEvent) => {
    e.stopPropagation()
    onDoubleClick(component.id)
    setShowMenu(false)
  }

  const handleConnectStart = (e: React.MouseEvent) => {
    e.stopPropagation()
    // TODO: Implement connection logic
    setShowMenu(false)
  }

  const handleContextMenu = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setShowMenu(!showMenu)
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
      className={`canvas-component ${simplifiedComp ? `canvas-component-${simplifiedComp.category}` : ''} ${isSelected ? 'selected' : ''} ${isDragging ? 'dragging' : ''}`}
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
      <div className="component-icon">{getIcon()}</div>
      <div
        className="component-label"
        style={colors ? { color: colors.text } : {}}
      >{component.label}</div>

      {showMenu && (
        <div className="component-menu">
          <button onClick={handleConfigure}>Configure</button>
          <button onClick={handleConnectStart}>Connect</button>
          <button onClick={handleDelete}>Delete</button>
        </div>
      )}

      {/* Connection points */}
      <div className="connection-point top" />
      <div className="connection-point right" />
      <div className="connection-point bottom" />
      <div className="connection-point left" />
    </div>
  )
}

export default CanvasComponent
