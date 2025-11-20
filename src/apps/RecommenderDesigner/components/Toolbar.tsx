import './Toolbar.css'

interface ToolbarProps {
  onClear: () => void
  componentCount: number
  connectionCount: number
  zoom: number
  onZoomIn: () => void
  onZoomOut: () => void
  onZoomReset: () => void
}

const Toolbar = ({
  onClear,
  componentCount,
  connectionCount,
  zoom,
  onZoomIn,
  onZoomOut,
  onZoomReset
}: ToolbarProps) => {
  return (
    <div className="toolbar">
      <div className="toolbar-section">
        <h2 className="toolbar-title">Recommender System Designer</h2>
      </div>
      <div className="toolbar-section toolbar-stats">
        <span className="stat-item">
          <span className="stat-label">Components:</span>
          <span className="stat-value">{componentCount}</span>
        </span>
        <span className="stat-item">
          <span className="stat-label">Connections:</span>
          <span className="stat-value">{connectionCount}</span>
        </span>
        <span className="stat-item">
          <span className="stat-label">Zoom:</span>
          <span className="stat-value">{Math.round(zoom * 100)}%</span>
        </span>
      </div>
      <div className="toolbar-section">
        <div className="zoom-controls">
          <button className="toolbar-button zoom-button" onClick={onZoomOut} title="Zoom Out">
            −
          </button>
          <button className="toolbar-button zoom-button" onClick={onZoomReset} title="Reset Zoom">
            100%
          </button>
          <button className="toolbar-button zoom-button" onClick={onZoomIn} title="Zoom In">
            +
          </button>
        </div>
        <button className="toolbar-button" onClick={onClear}>
          Clear Canvas
        </button>
      </div>
    </div>
  )
}

export default Toolbar
