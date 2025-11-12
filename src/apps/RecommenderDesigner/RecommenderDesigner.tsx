import { useState, useCallback } from 'react'
import { DndProvider } from 'react-dnd'
import { HTML5Backend } from 'react-dnd-html5-backend'
import Canvas from './components/Canvas'
import ComponentPalette from './components/ComponentPalette'
import Toolbar from './components/Toolbar'
import ConfigPanel from './components/ConfigPanel'
import { ComponentData, Connection } from './types'
import './RecommenderDesigner.css'

const RecommenderDesigner = () => {
  const [components, setComponents] = useState<ComponentData[]>([])
  const [connections, setConnections] = useState<Connection[]>([])
  const [selectedComponent, setSelectedComponent] = useState<string | null>(null)
  const [configPanelComponent, setConfigPanelComponent] = useState<ComponentData | null>(null)
  const [zoom, setZoom] = useState(1)
  const [pan, setPan] = useState({ x: 0, y: 0 })

  const addComponent = useCallback((component: ComponentData) => {
    setComponents(prev => [...prev, component])
  }, [])

  const updateComponent = useCallback((id: string, updates: Partial<ComponentData>) => {
    setComponents(prev =>
      prev.map(comp => (comp.id === id ? { ...comp, ...updates } : comp))
    )
  }, [])

  const updateComponentConfig = useCallback((id: string, config: Record<string, unknown>) => {
    updateComponent(id, { config })
  }, [updateComponent])

  const removeComponent = useCallback((id: string) => {
    setComponents(prev => prev.filter(comp => comp.id !== id))
    setConnections(prev => prev.filter(conn => conn.from !== id && conn.to !== id))
    if (selectedComponent === id) {
      setSelectedComponent(null)
    }
  }, [selectedComponent])

  const addConnection = useCallback((from: string, to: string) => {
    const id = `${from}-${to}`
    setConnections(prev => {
      if (prev.some(conn => conn.id === id)) {
        return prev
      }
      return [...prev, { id, from, to }]
    })
  }, [])

  const removeConnection = useCallback((id: string) => {
    setConnections(prev => prev.filter(conn => conn.id !== id))
  }, [])

  const clearCanvas = useCallback(() => {
    setComponents([])
    setConnections([])
    setSelectedComponent(null)
  }, [])

  const handleZoomIn = useCallback(() => {
    setZoom(prev => Math.min(prev + 0.1, 3))
  }, [])

  const handleZoomOut = useCallback(() => {
    setZoom(prev => Math.max(prev - 0.1, 0.3))
  }, [])

  const handleZoomReset = useCallback(() => {
    setZoom(1)
    setPan({ x: 0, y: 0 })
  }, [])

  const handleComponentDoubleClick = useCallback((id: string) => {
    const component = components.find(c => c.id === id)
    if (component) {
      setConfigPanelComponent(component)
    }
  }, [components])

  const handleCloseConfigPanel = useCallback(() => {
    setConfigPanelComponent(null)
  }, [])

  return (
    <DndProvider backend={HTML5Backend}>
      <div className="recommender-designer">
        <Toolbar
          onClear={clearCanvas}
          componentCount={components.length}
          connectionCount={connections.length}
          zoom={zoom}
          onZoomIn={handleZoomIn}
          onZoomOut={handleZoomOut}
          onZoomReset={handleZoomReset}
        />
        <div className="designer-content">
          <ComponentPalette />
          <Canvas
            components={components}
            connections={connections}
            selectedComponent={selectedComponent}
            zoom={zoom}
            pan={pan}
            onZoomChange={setZoom}
            onPanChange={setPan}
            onAddComponent={addComponent}
            onUpdateComponent={updateComponent}
            onRemoveComponent={removeComponent}
            onSelectComponent={setSelectedComponent}
            onAddConnection={addConnection}
            onRemoveConnection={removeConnection}
            onComponentDoubleClick={handleComponentDoubleClick}
          />
        </div>
        {configPanelComponent && (
          <ConfigPanel
            component={configPanelComponent}
            onUpdateConfig={updateComponentConfig}
            onClose={handleCloseConfigPanel}
          />
        )}
      </div>
    </DndProvider>
  )
}

export default RecommenderDesigner
