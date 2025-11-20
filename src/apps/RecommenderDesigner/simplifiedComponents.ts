/**
 * Simplified Component System for Recommender Designer
 *
 * Reduced to bare minimum essential blocks with logical flow:
 * INPUT → TRANSFORM → MODEL → OUTPUT
 */

export interface SimplifiedComponentDefinition {
  type: string
  label: string
  icon: string
  category: 'input' | 'transform' | 'model' | 'output'
  color: string
  description: string
  accepts: string[]  // What component types can connect as inputs
  produces: string   // What this component outputs
}

// Modern color palette - carefully chosen for accessibility and aesthetics
export const COLOR_PALETTE = {
  // Input blocks - Cool blues and teals
  input: {
    primary: '#3B82F6',      // Blue 500
    secondary: '#60A5FA',    // Blue 400
    gradient: 'linear-gradient(135deg, #3B82F6 0%, #60A5FA 100%)',
    border: '#2563EB',       // Blue 600
    text: '#FFFFFF'
  },
  // Transform blocks - Purples
  transform: {
    primary: '#8B5CF6',      // Violet 500
    secondary: '#A78BFA',    // Violet 400
    gradient: 'linear-gradient(135deg, #8B5CF6 0%, #A78BFA 100%)',
    border: '#7C3AED',       // Violet 600
    text: '#FFFFFF'
  },
  // Model blocks - Warm oranges and reds
  model: {
    primary: '#F59E0B',      // Amber 500
    secondary: '#FBBF24',    // Amber 400
    gradient: 'linear-gradient(135deg, #F59E0B 0%, #FBBF24 100%)',
    border: '#D97706',       // Amber 600
    text: '#000000'
  },
  // Output blocks - Greens
  output: {
    primary: '#10B981',      // Emerald 500
    secondary: '#34D399',    // Emerald 400
    gradient: 'linear-gradient(135deg, #10B981 0%, #34D399 100%)',
    border: '#059669',       // Emerald 600
    text: '#FFFFFF'
  }
}

/**
 * Simplified Component Catalog
 * Only the essential blocks needed for a complete recommender system
 */
export const SIMPLIFIED_COMPONENTS: SimplifiedComponentDefinition[] = [
  // ============================================================================
  // INPUT BLOCKS (Blue) - Data sources
  // ============================================================================
  {
    type: 'data-input',
    label: 'Data Source',
    icon: '📊',
    category: 'input',
    color: COLOR_PALETTE.input.gradient,
    description: 'Load user-item interaction data (ratings, clicks, purchases)',
    accepts: [],
    produces: 'dataframe'
  },
  {
    type: 'features-input',
    label: 'Features',
    icon: '🏷️',
    category: 'input',
    color: COLOR_PALETTE.input.gradient,
    description: 'User/item metadata and features (demographics, content, etc.)',
    accepts: [],
    produces: 'features'
  },

  // ============================================================================
  // TRANSFORM BLOCKS (Purple) - Data processing
  // ============================================================================
  {
    type: 'split',
    label: 'Train/Test Split',
    icon: '✂️',
    category: 'transform',
    color: COLOR_PALETTE.transform.gradient,
    description: 'Split data into training and test sets',
    accepts: ['dataframe'],
    produces: 'split-data'
  },
  {
    type: 'preprocessor',
    label: 'Preprocessor',
    icon: '🔧',
    category: 'transform',
    color: COLOR_PALETTE.transform.gradient,
    description: 'Clean, normalize, and transform data',
    accepts: ['dataframe', 'features'],
    produces: 'processed-data'
  },

  // ============================================================================
  // MODEL BLOCKS (Amber/Orange) - Machine learning algorithms
  // ============================================================================
  {
    type: 'collaborative-filtering',
    label: 'Collaborative Filter',
    icon: '🤝',
    category: 'model',
    color: COLOR_PALETTE.model.gradient,
    description: 'User-based or item-based collaborative filtering',
    accepts: ['split-data', 'processed-data'],
    produces: 'model'
  },
  {
    type: 'matrix-factorization',
    label: 'Matrix Factorization',
    icon: '🔢',
    category: 'model',
    color: COLOR_PALETTE.model.gradient,
    description: 'SVD, ALS, NMF - latent factor models',
    accepts: ['split-data', 'processed-data'],
    produces: 'model'
  },
  {
    type: 'xgboost',
    label: 'XGBoost',
    icon: '🚀',
    category: 'model',
    color: COLOR_PALETTE.model.gradient,
    description: 'Gradient boosting decision trees',
    accepts: ['split-data', 'processed-data', 'features'],
    produces: 'model'
  },
  {
    type: 'random-forest',
    label: 'Random Forest',
    icon: '🌲',
    category: 'model',
    color: COLOR_PALETTE.model.gradient,
    description: 'Ensemble of decision trees',
    accepts: ['split-data', 'processed-data', 'features'],
    produces: 'model'
  },
  {
    type: 'deep-learning',
    label: 'Neural Network',
    icon: '🧠',
    category: 'model',
    color: COLOR_PALETTE.model.gradient,
    description: 'Deep neural network models (NCF, DeepFM, etc.)',
    accepts: ['split-data', 'processed-data', 'features'],
    produces: 'model'
  },

  // ============================================================================
  // OUTPUT BLOCKS (Green) - Results and evaluation
  // ============================================================================
  {
    type: 'predictions',
    label: 'Predictions',
    icon: '🎯',
    category: 'output',
    color: COLOR_PALETTE.output.gradient,
    description: 'Generate top-K recommendations for users',
    accepts: ['model'],
    produces: 'recommendations'
  },
  {
    type: 'evaluation',
    label: 'Evaluation',
    icon: '📈',
    category: 'output',
    color: COLOR_PALETTE.output.gradient,
    description: 'Evaluate model performance (RMSE, Precision, NDCG, etc.)',
    accepts: ['model'],
    produces: 'metrics'
  }
]

/**
 * Example Workflow Combinations
 * These are validated block combinations that create complete pipelines
 */
export const EXAMPLE_WORKFLOWS = [
  {
    name: 'Simple Collaborative Filtering',
    description: 'Basic user-based recommendation system',
    blocks: [
      'data-input',
      'split',
      'collaborative-filtering',
      'predictions',
      'evaluation'
    ]
  },
  {
    name: 'XGBoost with Features',
    description: 'Gradient boosting with user/item features',
    blocks: [
      'data-input',
      'features-input',
      'split',
      'preprocessor',
      'xgboost',
      'predictions',
      'evaluation'
    ]
  },
  {
    name: 'Matrix Factorization Pipeline',
    description: 'SVD-based collaborative filtering',
    blocks: [
      'data-input',
      'split',
      'matrix-factorization',
      'predictions',
      'evaluation'
    ]
  },
  {
    name: 'Deep Learning Pipeline',
    description: 'Neural network with metadata features',
    blocks: [
      'data-input',
      'features-input',
      'split',
      'preprocessor',
      'deep-learning',
      'predictions',
      'evaluation'
    ]
  },
  {
    name: 'Model Comparison',
    description: 'Compare multiple models on same data',
    blocks: [
      'data-input',
      'split',
      'xgboost',
      'random-forest',
      'collaborative-filtering',
      'evaluation'
    ]
  }
]

/**
 * Validate if a connection between two components is allowed
 */
export function isValidConnection(
  fromType: string,
  toType: string
): boolean {
  const toComponent = SIMPLIFIED_COMPONENTS.find(c => c.type === toType)
  if (!toComponent) return false

  const fromComponent = SIMPLIFIED_COMPONENTS.find(c => c.type === fromType)
  if (!fromComponent) return false

  // Check if the destination accepts the output type of the source
  return toComponent.accepts.includes(fromComponent.produces) ||
         toComponent.accepts.length === 0  // Empty accepts means it can be a starting point
}

/**
 * Get component by type
 */
export function getSimplifiedComponent(type: string): SimplifiedComponentDefinition | undefined {
  return SIMPLIFIED_COMPONENTS.find(c => c.type === type)
}

/**
 * Get components by category
 */
export function getComponentsByCategory(category: string): SimplifiedComponentDefinition[] {
  return SIMPLIFIED_COMPONENTS.filter(c => c.category === category)
}

/**
 * Get color for component
 */
export function getComponentColor(category: string) {
  switch (category) {
    case 'input':
      return COLOR_PALETTE.input
    case 'transform':
      return COLOR_PALETTE.transform
    case 'model':
      return COLOR_PALETTE.model
    case 'output':
      return COLOR_PALETTE.output
    default:
      return COLOR_PALETTE.transform
  }
}
