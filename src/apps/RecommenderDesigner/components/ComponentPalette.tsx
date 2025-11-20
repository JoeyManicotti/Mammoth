import { SIMPLIFIED_COMPONENTS, getComponentsByCategory, EXAMPLE_WORKFLOWS } from '../simplifiedComponents'
import PaletteItem from './PaletteItem'
import './ComponentPalette.css'

const ComponentPalette = () => {
  const categories = [
    { key: 'input', label: 'Input', emoji: '📥', description: 'Data sources' },
    { key: 'transform', label: 'Transform', emoji: '⚙️', description: 'Data processing' },
    { key: 'model', label: 'Model', emoji: '🤖', description: 'ML algorithms' },
    { key: 'output', label: 'Output', emoji: '📤', description: 'Results & metrics' }
  ] as const

  return (
    <div className="component-palette">
      <div className="palette-header">
        <h3>Component Library</h3>
        <p>Drag blocks to canvas</p>
      </div>

      <div className="palette-content">
        {/* Components by Category */}
        {categories.map(category => {
          const components = getComponentsByCategory(category.key)
          return (
            <div key={category.key} className="palette-category">
              <h4 className="category-title">
                <span className="category-emoji">{category.emoji}</span>
                {category.label}
                <span className="category-description">{category.description}</span>
              </h4>
              <div className="category-items">
                {components.map(component => (
                  <PaletteItem key={component.type} definition={component} />
                ))}
              </div>
            </div>
          )
        })}

        {/* Example Workflows */}
        <div className="palette-section workflows-section">
          <h4 className="section-title">
            <span className="category-emoji">💡</span>
            Example Workflows
          </h4>
          {EXAMPLE_WORKFLOWS.map((workflow, idx) => (
            <details key={idx} className="workflow-example">
              <summary className="workflow-summary">
                {workflow.name}
              </summary>
              <div className="workflow-content">
                <p className="workflow-description">{workflow.description}</p>
                <div className="workflow-blocks">
                  {workflow.blocks.map((blockType, i) => {
                    const component = SIMPLIFIED_COMPONENTS.find(c => c.type === blockType)
                    return (
                      <div key={i} className="workflow-block">
                        <span className="workflow-block-icon">{component?.icon}</span>
                        <span className="workflow-block-label">{component?.label}</span>
                        {i < workflow.blocks.length - 1 && <span className="workflow-arrow">→</span>}
                      </div>
                    )
                  })}
                </div>
              </div>
            </details>
          ))}
        </div>

        {/* Quick Stats */}
        <div className="palette-stats">
          <div className="stat-pill">
            <span className="stat-number">{SIMPLIFIED_COMPONENTS.length}</span>
            <span className="stat-label">Total Blocks</span>
          </div>
          <div className="stat-pill">
            <span className="stat-number">{EXAMPLE_WORKFLOWS.length}</span>
            <span className="stat-label">Templates</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ComponentPalette
