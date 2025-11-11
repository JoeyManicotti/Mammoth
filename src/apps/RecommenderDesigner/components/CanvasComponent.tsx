import { useState } from 'react'
import { useDrag } from 'react-dnd'
import { ComponentData } from '../types'
import './CanvasComponent.css'

interface CanvasComponentProps {
  component: ComponentData
  isSelected: boolean
  onUpdate: (id: string, updates: Partial<ComponentData>) => void
  onRemove: (id: string) => void
  onSelect: (id: string) => void
  onConnect: (from: string, to: string) => void
  allComponents: ComponentData[]
}

const CanvasComponent = ({
  component,
  isSelected,
  onUpdate,
  onRemove,
  onSelect,
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

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation()
    onRemove(component.id)
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

  return (
    <div
      ref={drag}
      className={`canvas-component ${isSelected ? 'selected' : ''} ${isDragging ? 'dragging' : ''}`}
      style={{
        left: component.position.x,
        top: component.position.y
      }}
      onClick={handleClick}
      onContextMenu={handleContextMenu}
    >
      <div className="component-icon">{getIcon()}</div>
      <div className="component-label">{component.label}</div>

      {showMenu && (
        <div className="component-menu">
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
