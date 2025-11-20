import { useState } from 'react'
import { SIMPLIFIED_COMPONENTS, getComponentsByCategory, EXAMPLE_WORKFLOWS } from '../simplifiedComponents'
import PaletteItem from './PaletteItem'
import './ComponentPalette.css'

interface ComponentPaletteProps {
  onLoadWorkflow?: (workflow: { name: string; blocks: string[]; description?: string }) => void
}

const ComponentPalette = ({ onLoadWorkflow }: ComponentPaletteProps) => {
  const [activeTab, setActiveTab] = useState<'components' | 'recipes'>('components')

  const categories = [
    { key: 'input', label: 'Input', emoji: '📥', description: 'Data sources' },
    { key: 'transform', label: 'Transform', emoji: '⚙️', description: 'Data processing' },
    { key: 'model', label: 'Model', emoji: '🤖', description: 'ML algorithms' },
    { key: 'output', label: 'Output', emoji: '📤', description: 'Results & metrics' }
  ] as const

  const handleLoadWorkflow = (workflow: typeof EXAMPLE_WORKFLOWS[0]) => {
    if (onLoadWorkflow) {
      onLoadWorkflow(workflow)
    }
  }

  return (
    <div className="component-palette">
      <div className="palette-header">
        <h3>Component Library</h3>
        <div className="palette-tabs">
          <button
            className={`palette-tab ${activeTab === 'components' ? 'active' : ''}`}
            onClick={() => setActiveTab('components')}
          >
            <span>📦</span> Components
          </button>
          <button
            className={`palette-tab ${activeTab === 'recipes' ? 'active' : ''}`}
            onClick={() => setActiveTab('recipes')}
          >
            <span>📋</span> Recipes
          </button>
        </div>
      </div>

      <div className="palette-content">
        {activeTab === 'components' && (
          <>
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
          </>
        )}

        {activeTab === 'recipes' && (
          <div className="recipes-tab">
            <p className="recipes-description">
              Click any recipe to load it onto the canvas
            </p>
            <div className="recipes-grid">
              {EXAMPLE_WORKFLOWS.map((workflow, idx) => (
                <div
                  key={idx}
                  className="recipe-card"
                  onClick={() => handleLoadWorkflow(workflow)}
                  title="Click to load this workflow"
                >
                  <div className="recipe-header">
                    <h4 className="recipe-name">{workflow.name}</h4>
                    <div className="recipe-badge">{workflow.blocks.length} blocks</div>
                  </div>
                  <p className="recipe-description">{workflow.description}</p>
                  <div className="recipe-blocks-preview">
                    {workflow.blocks.slice(0, 4).map((blockType, i) => {
                      const component = SIMPLIFIED_COMPONENTS.find(c => c.type === blockType)
                      return (
                        <span key={i} className="recipe-block-icon" title={component?.label}>
                          {component?.icon}
                        </span>
                      )
                    })}
                    {workflow.blocks.length > 4 && (
                      <span className="recipe-more">+{workflow.blocks.length - 4}</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default ComponentPalette
