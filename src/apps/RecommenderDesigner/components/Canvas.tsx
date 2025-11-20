import { useRef, useCallback, useState } from 'react'
import { useDrop } from 'react-dnd'
import CanvasComponent from './CanvasComponent'
import ConnectionLine from './ConnectionLine'
import { ComponentData, Connection, ComponentDefinition } from '../types'
import './Canvas.css'

interface CanvasProps {
  components: ComponentData[]
  connections: Connection[]
  selectedComponent: string | null
  connectingFrom: string | null
  zoom: number
  pan: { x: number; y: number }
  onZoomChange: (zoom: number) => void
  onPanChange: (pan: { x: number; y: number }) => void
  onAddComponent: (component: ComponentData) => void
  onUpdateComponent: (id: string, updates: Partial<ComponentData>) => void
  onRemoveComponent: (id: string) => void
  onSelectComponent: (id: string | null) => void
  onAddConnection: (from: string, to: string) => void
  onRemoveConnection: (id: string) => void
  onComponentDoubleClick: (id: string) => void
  onSetConnectingFrom: (id: string | null) => void
}

const Canvas = ({
  components,
  connections,
  selectedComponent,
  connectingFrom,
  zoom,
  pan,
  onZoomChange,
  onPanChange,
  onAddComponent,
  onUpdateComponent,
  onRemoveComponent,
  onSelectComponent,
  onAddConnection,
  onRemoveConnection,
  onComponentDoubleClick,
  onSetConnectingFrom
}: CanvasProps) => {
  const componentCounter = useRef(0)
  const [isPanning, setIsPanning] = useState(false)
  const [panStart, setPanStart] = useState({ x: 0, y: 0 })

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
    if (e.target === e.currentTarget || (e.target as HTMLElement).classList.contains('canvas-content')) {
      onSelectComponent(null)
    }
  }, [onSelectComponent])

  const handleWheel = useCallback((e: React.WheelEvent) => {
    e.preventDefault()
    const delta = e.deltaY > 0 ? -0.1 : 0.1
    const newZoom = Math.max(0.3, Math.min(3, zoom + delta))
    onZoomChange(newZoom)
  }, [zoom, onZoomChange])

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    if (e.button === 1 || (e.button === 0 && e.shiftKey)) { // Middle click or Shift + Left click
      e.preventDefault()
      setIsPanning(true)
      setPanStart({ x: e.clientX - pan.x, y: e.clientY - pan.y })
    }
  }, [pan])

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (isPanning) {
      onPanChange({
        x: e.clientX - panStart.x,
        y: e.clientY - panStart.y
      })
    }
  }, [isPanning, panStart, onPanChange])

  const handleMouseUp = useCallback(() => {
    setIsPanning(false)
  }, [])

  const getComponentCenter = (component: ComponentData) => {
    return {
      x: component.position.x + 75, // half of component width (150px)
      y: component.position.y + 40  // half of component height (80px)
    }
  }

  return (
    <div
      ref={drop}
      className={`canvas ${isOver ? 'drag-over' : ''} ${isPanning ? 'panning' : ''}`}
      onClick={handleCanvasClick}
      onWheel={handleWheel}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
    >
      <div className="canvas-grid" />

      <div
        className="canvas-content"
        style={{
          transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
          transformOrigin: '0 0'
        }}
      >
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
            isConnecting={connectingFrom === component.id}
            onUpdate={onUpdateComponent}
            onRemove={onRemoveComponent}
            onSelect={onSelectComponent}
            onConnect={onAddConnection}
            onDoubleClick={onComponentDoubleClick}
            onStartConnection={onSetConnectingFrom}
            connectingFrom={connectingFrom}
            allComponents={components}
          />
        ))}

        {components.length === 0 && !isOver && (
          <div className="canvas-placeholder">
            <p>Drag components from the palette to start designing</p>
            <p className="canvas-hint">Use mouse wheel to zoom • Shift + drag to pan</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default Canvas
