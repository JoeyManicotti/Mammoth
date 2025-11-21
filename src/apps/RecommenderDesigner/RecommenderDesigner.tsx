import { useState, useCallback, useEffect, useRef } from 'react'
import { DndProvider } from 'react-dnd'
import { HTML5Backend } from 'react-dnd-html5-backend'
import Canvas from './components/Canvas'
import ComponentPalette from './components/ComponentPalette'
import Toolbar from './components/Toolbar'
import ConfigPanel from './components/ConfigPanel'
import HelpModal from './components/HelpModal'
import { ComponentData, Connection } from './types'
import { getSimplifiedComponent } from './simplifiedComponents'
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
  const [paletteCollapsed, setPaletteCollapsed] = useState(false)
  const [paletteWidth, setPaletteWidth] = useState(300)
  const [isResizing, setIsResizing] = useState(false)
  const [workflowStatus, setWorkflowStatus] = useState<string>('')
  const componentCounter = useRef(0)

  // Load canvas and UI state from localStorage on mount
  useEffect(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY)
      if (saved) {
        const data = JSON.parse(saved)
        setComponents(data.components || [])
        setConnections(data.connections || [])
        if (data.uiState) {
          setPaletteCollapsed(data.uiState.paletteCollapsed || false)
          setPaletteWidth(data.uiState.paletteWidth || 300)
        }
      }
    } catch (error) {
      console.error('Failed to load canvas from storage:', error)
    }
  }, [])

  // Auto-save canvas and UI state to localStorage whenever it changes
  useEffect(() => {
    try {
      const data = {
        components,
        connections,
        uiState: {
          paletteCollapsed,
          paletteWidth
        },
        savedAt: new Date().toISOString()
      }
      localStorage.setItem(STORAGE_KEY, JSON.stringify(data))
    } catch (error) {
      console.error('Failed to save canvas to storage:', error)
    }
  }, [components, connections, paletteCollapsed, paletteWidth])

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

  const handleLoadWorkflow = useCallback((workflow: { name: string; blocks: string[]; description?: string }) => {
    // Clear existing canvas
    setComponents([])
    setConnections([])
    setSelectedComponent(null)

    // Create components for each block
    const newComponents: ComponentData[] = []
    const newConnections: Connection[] = []

    const startX = 100
    const startY = 100
    const horizontalSpacing = 220
    const verticalSpacing = 140

    workflow.blocks.forEach((blockType, index) => {
      const componentDef = getSimplifiedComponent(blockType)
      if (!componentDef) return

      componentCounter.current += 1

      // Calculate position in a flowing layout
      const row = Math.floor(index / 4)
      const col = index % 4
      const x = startX + col * horizontalSpacing
      const y = startY + row * verticalSpacing

      const newComponent: ComponentData = {
        id: `component-${componentCounter.current}`,
        type: blockType as ComponentData['type'],
        label: componentDef.label,
        position: { x, y }
      }

      newComponents.push(newComponent)

      // Create connection to previous component
      if (index > 0) {
        const prevComponent = newComponents[index - 1]
        newConnections.push({
          id: `${prevComponent.id}-${newComponent.id}`,
          from: prevComponent.id,
          to: newComponent.id
        })
      }
    })

    setComponents(newComponents)
    setConnections(newConnections)

    // Reset zoom and pan
    setZoom(1)
    setPan({ x: 0, y: 0 })
  }, [])

  const handleRunWorkflow = useCallback((workflow: { name: string; blocks: string[]; description?: string }) => {
    // First, load the workflow onto the canvas
    handleLoadWorkflow(workflow)

    // Show running status
    setWorkflowStatus(`Running "${workflow.name}"...`)

    // Simulate workflow execution
    setTimeout(() => {
      setWorkflowStatus(`Successfully executed "${workflow.name}" with ${workflow.blocks.length} blocks`)

      // Clear status after 5 seconds
      setTimeout(() => {
        setWorkflowStatus('')
      }, 5000)
    }, 1000)
  }, [handleLoadWorkflow])

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    setIsResizing(true)
    e.preventDefault()
  }, [])

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (isResizing) {
      const newWidth = Math.max(200, Math.min(600, e.clientX))
      setPaletteWidth(newWidth)
    }
  }, [isResizing])

  const handleMouseUp = useCallback(() => {
    setIsResizing(false)
  }, [])

  useEffect(() => {
    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove)
      document.addEventListener('mouseup', handleMouseUp)
      return () => {
        document.removeEventListener('mousemove', handleMouseMove)
        document.removeEventListener('mouseup', handleMouseUp)
      }
    }
  }, [isResizing, handleMouseMove, handleMouseUp])

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
          {!paletteCollapsed && (
            <div
              className="resizable-palette"
              style={{ width: paletteWidth }}
            >
              <ComponentPalette
                onLoadWorkflow={handleLoadWorkflow}
                onRunWorkflow={handleRunWorkflow}
              />
              <div
                className="resize-handle"
                onMouseDown={handleMouseDown}
              />
            </div>
          )}
          <button
            className={`palette-toggle ${paletteCollapsed ? 'collapsed' : ''}`}
            onClick={() => setPaletteCollapsed(!paletteCollapsed)}
            title={paletteCollapsed ? 'Show component palette' : 'Hide component palette'}
          >
            {paletteCollapsed ? '▶' : '◀'}
          </button>
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
        {workflowStatus && (
          <div className="workflow-status-toast">
            {workflowStatus}
          </div>
        )}
      </div>
    </DndProvider>
  )
}

export default RecommenderDesigner
