import './Toolbar.css'

interface ToolbarProps {
  onClear: () => void
  componentCount: number
  connectionCount: number
}

const Toolbar = ({ onClear, componentCount, connectionCount }: ToolbarProps) => {
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
      </div>
      <div className="toolbar-section">
        <button className="toolbar-button" onClick={onClear}>
          Clear Canvas
        </button>
      </div>
    </div>
  )
}

export default Toolbar
