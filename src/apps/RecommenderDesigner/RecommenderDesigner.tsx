import { useState, useCallback, useEffect } from 'react'
import { DndProvider } from 'react-dnd'
import { HTML5Backend } from 'react-dnd-html5-backend'
import Canvas from './components/Canvas'
import ComponentPalette from './components/ComponentPalette'
import Toolbar from './components/Toolbar'
import ConfigPanel from './components/ConfigPanel'
import HelpModal from './components/HelpModal'
import { ComponentData, Connection } from './types'
import './RecommenderDesigner.css'

const STORAGE_KEY = 'mammoth-recommender-canvas'

const RecommenderDesigner = () => {
  const [components, setComponents] = useState<ComponentData[]>([])
  const [connections, setConnections] = useState<Connection[]>([])
  const [selectedComponent, setSelectedComponent] = useState<string | null>(null)
  const [configPanelComponent, setConfigPanelComponent] = useState<ComponentData | null>(null)
  const [connectingFrom, setConnectingFrom] = useState<string | null>(null)
  const [showHelp, setShowHelp] = useState(false)
  const [zoom, setZoom] = useState(1)
  const [pan, setPan] = useState({ x: 0, y: 0 })

  // Load canvas from localStorage on mount
  useEffect(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY)
      if (saved) {
        const data = JSON.parse(saved)
        setComponents(data.components || [])
        setConnections(data.connections || [])
      }
    } catch (error) {
      console.error('Failed to load canvas from storage:', error)
    }
  }, [])

  // Auto-save canvas to localStorage whenever it changes
  useEffect(() => {
    try {
      const data = {
        components,
        connections,
        savedAt: new Date().toISOString()
      }
      localStorage.setItem(STORAGE_KEY, JSON.stringify(data))
    } catch (error) {
      console.error('Failed to save canvas to storage:', error)
    }
  }, [components, connections])

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

  const handleSaveToFile = useCallback(() => {
    const data = {
      components,
      connections,
      version: '1.0',
      savedAt: new Date().toISOString()
    }

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `mammoth-workflow-${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }, [components, connections])

  const handleLoadFromFile = useCallback(() => {
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = '.json'

    input.onchange = (e) => {
      const file = (e.target as HTMLInputElement).files?.[0]
      if (file) {
        const reader = new FileReader()
        reader.onload = (event) => {
          try {
            const data = JSON.parse(event.target?.result as string)
            setComponents(data.components || [])
            setConnections(data.connections || [])
          } catch (error) {
            console.error('Failed to load workflow file:', error)
            alert('Failed to load workflow file. Please check the file format.')
          }
        }
        reader.readAsText(file)
      }
    }

    input.click()
  }, [])

  return (
    <DndProvider backend={HTML5Backend}>
      <div className="recommender-designer">
        <Toolbar
          onClear={clearCanvas}
          onSave={handleSaveToFile}
          onLoad={handleLoadFromFile}
          onHelp={() => setShowHelp(true)}
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
            connectingFrom={connectingFrom}
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
            onSetConnectingFrom={setConnectingFrom}
          />
        </div>
        {configPanelComponent && (
          <ConfigPanel
            component={configPanelComponent}
            onUpdateConfig={updateComponentConfig}
            onClose={handleCloseConfigPanel}
          />
        )}
        {showHelp && (
          <HelpModal onClose={() => setShowHelp(false)} />
        )}
      </div>
    </DndProvider>
  )
}

export default RecommenderDesigner
