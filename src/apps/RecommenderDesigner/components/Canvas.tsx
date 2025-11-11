import { useRef, useCallback } from 'react'
import { useDrop } from 'react-dnd'
import CanvasComponent from './CanvasComponent'
import ConnectionLine from './ConnectionLine'
import { ComponentData, Connection, ComponentDefinition } from '../types'
import './Canvas.css'

interface CanvasProps {
  components: ComponentData[]
  connections: Connection[]
  selectedComponent: string | null
  onAddComponent: (component: ComponentData) => void
  onUpdateComponent: (id: string, updates: Partial<ComponentData>) => void
  onRemoveComponent: (id: string) => void
  onSelectComponent: (id: string | null) => void
  onAddConnection: (from: string, to: string) => void
  onRemoveConnection: (id: string) => void
}

const Canvas = ({
  components,
  connections,
  selectedComponent,
  onAddComponent,
  onUpdateComponent,
  onRemoveComponent,
  onSelectComponent,
  onAddConnection,
  onRemoveConnection
}: CanvasProps) => {
  const componentCounter = useRef(0)

  const [{ isOver }, drop] = useDrop(() => ({
    accept: 'component',
    drop: (item: { definition: ComponentDefinition }, monitor) => {
      const offset = monitor.getClientOffset()

      if (offset) {
        const canvasElement = document.querySelector('.canvas')
        const canvasRect = canvasElement?.getBoundingClientRect()

        if (canvasRect) {
          const x = offset.x - canvasRect.left
          const y = offset.y - canvasRect.top

          componentCounter.current = componentCounter.current + 1

          const newComponent: ComponentData = {
            id: `component-${componentCounter.current}`,
            type: item.definition.type,
            label: item.definition.label,
            position: { x, y }
          }

          onAddComponent(newComponent)
        }
      }
    },
    collect: (monitor) => ({
      isOver: monitor.isOver()
    })
  }), [onAddComponent])

  const handleCanvasClick = useCallback((e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onSelectComponent(null)
    }
  }, [onSelectComponent])

  const getComponentCenter = (component: ComponentData) => {
    return {
      x: component.position.x + 75, // half of component width (150px)
      y: component.position.y + 40  // half of component height (80px)
    }
  }

  return (
    <div
      ref={drop}
      className={`canvas ${isOver ? 'drag-over' : ''}`}
      onClick={handleCanvasClick}
    >
      <div className="canvas-grid" />

      {/* Render connections */}
      <svg className="connections-layer">
        {connections.map(connection => {
          const fromComponent = components.find(c => c.id === connection.from)
          const toComponent = components.find(c => c.id === connection.to)

          if (!fromComponent || !toComponent) return null

          const from = getComponentCenter(fromComponent)
          const to = getComponentCenter(toComponent)

          return (
            <ConnectionLine
              key={connection.id}
              id={connection.id}
              from={from}
              to={to}
              onRemove={() => onRemoveConnection(connection.id)}
            />
          )
        })}
      </svg>

      {/* Render components */}
      {components.map(component => (
        <CanvasComponent
          key={component.id}
          component={component}
          isSelected={selectedComponent === component.id}
          onUpdate={onUpdateComponent}
          onRemove={onRemoveComponent}
          onSelect={onSelectComponent}
          onConnect={onAddConnection}
          allComponents={components}
        />
      ))}

      {components.length === 0 && !isOver && (
        <div className="canvas-placeholder">
          <p>Drag components from the palette to start designing</p>
        </div>
      )}
    </div>
  )
}

export default Canvas
