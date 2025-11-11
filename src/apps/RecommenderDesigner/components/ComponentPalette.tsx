import { ComponentDefinition } from '../types'
import PaletteItem from './PaletteItem'
import './ComponentPalette.css'

const componentDefinitions: ComponentDefinition[] = [
  {
    type: 'data-source',
    label: 'Data Source',
    icon: '📊',
    category: 'data',
    description: 'Input data source'
  },
  {
    type: 'user-profile',
    label: 'User Profile',
    icon: '👤',
    category: 'data',
    description: 'User information and preferences'
  },
  {
    type: 'item-catalog',
    label: 'Item Catalog',
    icon: '📦',
    category: 'data',
    description: 'Available items to recommend'
  },
  {
    type: 'feature-extraction',
    label: 'Feature Extraction',
    icon: '🔍',
    category: 'processing',
    description: 'Extract features from raw data'
  },
  {
    type: 'collaborative-filter',
    label: 'Collaborative Filter',
    icon: '🤝',
    category: 'algorithm',
    description: 'User-based or item-based filtering'
  },
  {
    type: 'content-filter',
    label: 'Content Filter',
    icon: '📝',
    category: 'algorithm',
    description: 'Content-based filtering'
  },
  {
    type: 'matrix-factorization',
    label: 'Matrix Factorization',
    icon: '🔢',
    category: 'algorithm',
    description: 'SVD, ALS, or similar techniques'
  },
  {
    type: 'deep-learning',
    label: 'Deep Learning',
    icon: '🧠',
    category: 'algorithm',
    description: 'Neural network models'
  },
  {
    type: 'ranking',
    label: 'Ranking',
    icon: '📈',
    category: 'processing',
    description: 'Score and rank recommendations'
  },
  {
    type: 'output',
    label: 'Output',
    icon: '📤',
    category: 'output',
    description: 'Final recommendations'
  },
  {
    type: 'evaluation',
    label: 'Evaluation',
    icon: '✅',
    category: 'output',
    description: 'Evaluate model performance'
  }
]

const ComponentPalette = () => {
  const categories = [
    { key: 'data', label: 'Data Sources' },
    { key: 'processing', label: 'Processing' },
    { key: 'algorithm', label: 'Algorithms' },
    { key: 'output', label: 'Output' }
  ] as const

  return (
    <div className="component-palette">
      <div className="palette-header">
        <h3>Components</h3>
        <p>Drag components to canvas</p>
      </div>
      <div className="palette-content">
        {categories.map(category => (
          <div key={category.key} className="palette-category">
            <h4 className="category-title">{category.label}</h4>
            <div className="category-items">
              {componentDefinitions
                .filter(def => def.category === category.key)
                .map(def => (
                  <PaletteItem key={def.type} definition={def} />
                ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default ComponentPalette
