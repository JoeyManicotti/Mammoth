/**
 * Component Specifications for Recommender System Designer
 *
 * This file defines detailed specifications for each component type including:
 * - Input/Output schemas
 * - Configuration options
 * - Test cases
 * - Expected behaviors
 */

export interface ComponentIO {
  name: string
  type: 'dataframe' | 'matrix' | 'vector' | 'model' | 'metrics' | 'config'
  schema?: Record<string, string>
  required: boolean
  description: string
}

export interface ComponentSpec {
  type: string
  name: string
  category: string
  description: string
  inputs: ComponentIO[]
  outputs: ComponentIO[]
  config: {
    name: string
    type: 'string' | 'number' | 'boolean' | 'select' | 'multiselect'
    default: unknown
    options?: string[]
    description: string
  }[]
  testCases: {
    name: string
    input: Record<string, unknown>
    config: Record<string, unknown>
    expectedOutput: Record<string, unknown>
    description: string
  }[]
  implementation?: string
}

export const COMPONENT_SPECIFICATIONS: Record<string, ComponentSpec> = {
  'data-source': {
    type: 'data-source',
    name: 'Data Source',
    category: 'data',
    description: 'Loads and provides raw data for the recommendation system',
    inputs: [],
    outputs: [
      {
        name: 'dataframe',
        type: 'dataframe',
        schema: {
          user_id: 'int',
          item_id: 'int',
          rating: 'float',
          timestamp: 'datetime'
        },
        required: true,
        description: 'Raw interaction data with user-item ratings'
      }
    ],
    config: [
      {
        name: 'dataSource',
        type: 'select',
        default: 'csv',
        options: ['csv', 'database', 'api', 'synthetic'],
        description: 'Source of the data'
      },
      {
        name: 'filePath',
        type: 'string',
        default: '',
        description: 'Path to data file (for CSV source)'
      },
      {
        name: 'sampleSize',
        type: 'number',
        default: 0,
        description: 'Number of rows to sample (0 for all)'
      }
    ],
    testCases: [
      {
        name: 'Load MovieLens 100K',
        input: {},
        config: {
          dataSource: 'csv',
          filePath: 'ml-100k/u.data',
          sampleSize: 0
        },
        expectedOutput: {
          dataframe: {
            rows: 100000,
            columns: ['user_id', 'item_id', 'rating', 'timestamp'],
            sample: [[196, 242, 3.0, 881250949]]
          }
        },
        description: 'Load full MovieLens 100K dataset'
      },
      {
        name: 'Generate synthetic data',
        input: {},
        config: {
          dataSource: 'synthetic',
          sampleSize: 1000
        },
        expectedOutput: {
          dataframe: {
            rows: 1000,
            columns: ['user_id', 'item_id', 'rating', 'timestamp']
          }
        },
        description: 'Generate 1000 synthetic interactions'
      }
    ]
  },

  'user-profile': {
    type: 'user-profile',
    name: 'User Profile',
    category: 'data',
    description: 'Manages user demographic and behavioral data',
    inputs: [
      {
        name: 'interactions',
        type: 'dataframe',
        required: true,
        description: 'User interaction history'
      }
    ],
    outputs: [
      {
        name: 'userFeatures',
        type: 'dataframe',
        schema: {
          user_id: 'int',
          age: 'int',
          gender: 'string',
          avg_rating: 'float',
          activity_level: 'string'
        },
        required: true,
        description: 'Enriched user profile features'
      }
    ],
    config: [
      {
        name: 'includeDemo graphics',
        type: 'boolean',
        default: true,
        description: 'Include demographic features'
      },
      {
        name: 'includeBehavioral',
        type: 'boolean',
        default: true,
        description: 'Include behavioral features'
      }
    ],
    testCases: [
      {
        name: 'Build user profiles',
        input: {
          interactions: {
            data: [[1, 101, 5.0], [1, 102, 4.0], [2, 101, 3.0]]
          }
        },
        config: {
          includeDemographics: true,
          includeBehavioral: true
        },
        expectedOutput: {
          userFeatures: {
            rows: 2,
            columns: ['user_id', 'age', 'gender', 'avg_rating', 'activity_level']
          }
        },
        description: 'Generate user profiles from interactions'
      }
    ]
  },

  'item-catalog': {
    type: 'item-catalog',
    name: 'Item Catalog',
    category: 'data',
    description: 'Manages item metadata and features',
    inputs: [],
    outputs: [
      {
        name: 'itemFeatures',
        type: 'dataframe',
        schema: {
          item_id: 'int',
          title: 'string',
          genres: 'list',
          release_year: 'int',
          popularity: 'float'
        },
        required: true,
        description: 'Item metadata and features'
      }
    ],
    config: [
      {
        name: 'includeContent',
        type: 'boolean',
        default: true,
        description: 'Include content-based features'
      },
      {
        name: 'includePopularity',
        type: 'boolean',
        default: true,
        description: 'Calculate popularity metrics'
      }
    ],
    testCases: [
      {
        name: 'Load item catalog',
        input: {},
        config: {
          includeContent: true,
          includePopularity: true
        },
        expectedOutput: {
          itemFeatures: {
            rows: 1682,
            columns: ['item_id', 'title', 'genres', 'release_year', 'popularity']
          }
        },
        description: 'Load MovieLens item metadata'
      }
    ]
  },

  'feature-extraction': {
    type: 'feature-extraction',
    name: 'Feature Extraction',
    category: 'processing',
    description: 'Extracts and transforms features from raw data',
    inputs: [
      {
        name: 'rawData',
        type: 'dataframe',
        required: true,
        description: 'Raw input data'
      }
    ],
    outputs: [
      {
        name: 'features',
        type: 'matrix',
        required: true,
        description: 'Extracted feature matrix'
      }
    ],
    config: [
      {
        name: 'method',
        type: 'select',
        default: 'tfidf',
        options: ['tfidf', 'word2vec', 'bert', 'manual'],
        description: 'Feature extraction method'
      },
      {
        name: 'normalize',
        type: 'boolean',
        default: true,
        description: 'Normalize features'
      }
    ],
    testCases: [
      {
        name: 'Extract TF-IDF features',
        input: {
          rawData: {
            data: [['Action|Adventure'], ['Comedy'], ['Action|Thriller']]
          }
        },
        config: {
          method: 'tfidf',
          normalize: true
        },
        expectedOutput: {
          features: {
            shape: [3, 4],
            sparse: true
          }
        },
        description: 'Extract TF-IDF features from genre strings'
      }
    ]
  },

  'collaborative-filter': {
    type: 'collaborative-filter',
    name: 'Collaborative Filtering',
    category: 'algorithm',
    description: 'User-based or item-based collaborative filtering',
    inputs: [
      {
        name: 'interactionMatrix',
        type: 'matrix',
        required: true,
        description: 'User-item interaction matrix'
      }
    ],
    outputs: [
      {
        name: 'predictions',
        type: 'matrix',
        required: true,
        description: 'Predicted ratings matrix'
      },
      {
        name: 'similarities',
        type: 'matrix',
        required: false,
        description: 'User/item similarity matrix'
      }
    ],
    config: [
      {
        name: 'method',
        type: 'select',
        default: 'user-based',
        options: ['user-based', 'item-based', 'hybrid'],
        description: 'Collaborative filtering approach'
      },
      {
        name: 'similarity',
        type: 'select',
        default: 'cosine',
        options: ['cosine', 'pearson', 'jaccard', 'euclidean'],
        description: 'Similarity metric'
      },
      {
        name: 'k_neighbors',
        type: 'number',
        default: 50,
        description: 'Number of neighbors to consider'
      }
    ],
    testCases: [
      {
        name: 'User-based CF with cosine similarity',
        input: {
          interactionMatrix: {
            shape: [943, 1682],
            nonzero: 100000
          }
        },
        config: {
          method: 'user-based',
          similarity: 'cosine',
          k_neighbors: 50
        },
        expectedOutput: {
          predictions: {
            shape: [943, 1682]
          },
          metrics: {
            rmse: { min: 0.85, max: 1.0 }
          }
        },
        description: 'User-based CF on MovieLens 100K'
      }
    ]
  },

  'matrix-factorization': {
    type: 'matrix-factorization',
    name: 'Matrix Factorization',
    category: 'algorithm',
    description: 'SVD, ALS, or NMF-based matrix factorization',
    inputs: [
      {
        name: 'interactionMatrix',
        type: 'matrix',
        required: true,
        description: 'User-item interaction matrix'
      }
    ],
    outputs: [
      {
        name: 'predictions',
        type: 'matrix',
        required: true,
        description: 'Predicted ratings matrix'
      },
      {
        name: 'userFactors',
        type: 'matrix',
        required: false,
        description: 'User latent factor matrix'
      },
      {
        name: 'itemFactors',
        type: 'matrix',
        required: false,
        description: 'Item latent factor matrix'
      }
    ],
    config: [
      {
        name: 'method',
        type: 'select',
        default: 'svd',
        options: ['svd', 'als', 'nmf', 'svdpp'],
        description: 'Factorization method'
      },
      {
        name: 'n_factors',
        type: 'number',
        default: 100,
        description: 'Number of latent factors'
      },
      {
        name: 'n_epochs',
        type: 'number',
        default: 20,
        description: 'Number of training epochs'
      },
      {
        name: 'learning_rate',
        type: 'number',
        default: 0.005,
        description: 'Learning rate for training'
      },
      {
        name: 'regularization',
        type: 'number',
        default: 0.02,
        description: 'Regularization parameter'
      }
    ],
    testCases: [
      {
        name: 'SVD on MovieLens',
        input: {
          interactionMatrix: {
            shape: [943, 1682],
            nonzero: 100000
          }
        },
        config: {
          method: 'svd',
          n_factors: 100,
          n_epochs: 20,
          learning_rate: 0.005,
          regularization: 0.02
        },
        expectedOutput: {
          predictions: {
            shape: [943, 1682]
          },
          metrics: {
            rmse: { min: 0.87, max: 0.95 },
            mae: { min: 0.68, max: 0.75 }
          }
        },
        description: 'SVD with 100 factors, 20 epochs'
      }
    ]
  },

  'deep-learning': {
    type: 'deep-learning',
    name: 'Deep Learning Model',
    category: 'algorithm',
    description: 'Neural collaborative filtering or deep recommendation models',
    inputs: [
      {
        name: 'userFeatures',
        type: 'matrix',
        required: true,
        description: 'User feature matrix'
      },
      {
        name: 'itemFeatures',
        type: 'matrix',
        required: true,
        description: 'Item feature matrix'
      },
      {
        name: 'interactions',
        type: 'dataframe',
        required: true,
        description: 'User-item interactions for training'
      }
    ],
    outputs: [
      {
        name: 'model',
        type: 'model',
        required: true,
        description: 'Trained neural network model'
      },
      {
        name: 'predictions',
        type: 'matrix',
        required: true,
        description: 'Predicted scores'
      }
    ],
    config: [
      {
        name: 'architecture',
        type: 'select',
        default: 'ncf',
        options: ['ncf', 'wide_deep', 'deepfm', 'autoint'],
        description: 'Model architecture'
      },
      {
        name: 'embedding_dim',
        type: 'number',
        default: 64,
        description: 'Embedding dimension'
      },
      {
        name: 'hidden_layers',
        type: 'string',
        default: '128,64,32',
        description: 'Hidden layer sizes (comma-separated)'
      },
      {
        name: 'dropout',
        type: 'number',
        default: 0.2,
        description: 'Dropout rate'
      },
      {
        name: 'batch_size',
        type: 'number',
        default: 256,
        description: 'Training batch size'
      },
      {
        name: 'epochs',
        type: 'number',
        default: 10,
        description: 'Number of training epochs'
      }
    ],
    testCases: [
      {
        name: 'NCF on MovieLens',
        input: {
          userFeatures: { shape: [943, 20] },
          itemFeatures: { shape: [1682, 30] },
          interactions: { rows: 100000 }
        },
        config: {
          architecture: 'ncf',
          embedding_dim: 64,
          hidden_layers: '128,64,32',
          dropout: 0.2,
          batch_size: 256,
          epochs: 10
        },
        expectedOutput: {
          model: { parameters: 50000 },
          predictions: { shape: [943, 1682] },
          metrics: {
            rmse: { min: 0.88, max: 0.96 },
            ndcg: { min: 0.32, max: 0.38 }
          }
        },
        description: 'Neural Collaborative Filtering with 3 hidden layers'
      }
    ]
  },

  'ranking': {
    type: 'ranking',
    name: 'Ranking',
    category: 'processing',
    description: 'Ranks and filters recommendations based on business rules',
    inputs: [
      {
        name: 'predictions',
        type: 'matrix',
        required: true,
        description: 'Raw prediction scores'
      },
      {
        name: 'constraints',
        type: 'dataframe',
        required: false,
        description: 'Business constraints and rules'
      }
    ],
    outputs: [
      {
        name: 'rankedItems',
        type: 'dataframe',
        required: true,
        description: 'Ranked list of recommendations per user'
      }
    ],
    config: [
      {
        name: 'topK',
        type: 'number',
        default: 10,
        description: 'Number of items to recommend per user'
      },
      {
        name: 'diversityWeight',
        type: 'number',
        default: 0.0,
        description: 'Weight for diversity (0-1)'
      },
      {
        name: 'freshness Boost',
        type: 'number',
        default: 0.0,
        description: 'Boost factor for recent items'
      }
    ],
    testCases: [
      {
        name: 'Top-10 recommendations',
        input: {
          predictions: { shape: [943, 1682] }
        },
        config: {
          topK: 10,
          diversityWeight: 0.1,
          freshnessBoost: 0.05
        },
        expectedOutput: {
          rankedItems: {
            rows: 9430,
            columns: ['user_id', 'item_id', 'score', 'rank']
          }
        },
        description: 'Generate top-10 recommendations with diversity'
      }
    ]
  },

  'evaluation': {
    type: 'evaluation',
    name: 'Evaluation',
    category: 'output',
    description: 'Evaluates recommendation quality using various metrics',
    inputs: [
      {
        name: 'predictions',
        type: 'matrix',
        required: true,
        description: 'Predicted scores or rankings'
      },
      {
        name: 'groundTruth',
        type: 'dataframe',
        required: true,
        description: 'Actual user-item interactions (test set)'
      }
    ],
    outputs: [
      {
        name: 'metrics',
        type: 'metrics',
        required: true,
        description: 'Evaluation metrics'
      }
    ],
    config: [
      {
        name: 'metrics',
        type: 'multiselect',
        default: ['rmse', 'mae', 'precision', 'recall', 'ndcg'],
        options: ['rmse', 'mae', 'precision', 'recall', 'ndcg', 'map', 'auc', 'coverage', 'diversity'],
        description: 'Metrics to compute'
      },
      {
        name: 'k_values',
        type: 'string',
        default: '5,10,20',
        description: 'K values for ranking metrics (comma-separated)'
      }
    ],
    testCases: [
      {
        name: 'Comprehensive evaluation',
        input: {
          predictions: { shape: [943, 1682] },
          groundTruth: { rows: 20000 }
        },
        config: {
          metrics: ['rmse', 'mae', 'precision', 'recall', 'ndcg'],
          k_values: '5,10,20'
        },
        expectedOutput: {
          metrics: {
            rmse: 0.92,
            mae: 0.73,
            'precision@10': 0.32,
            'recall@10': 0.18,
            'ndcg@10': 0.35
          }
        },
        description: 'Compute multiple evaluation metrics'
      }
    ]
  }
}

export function getComponentSpec(type: string): ComponentSpec | undefined {
  return COMPONENT_SPECIFICATIONS[type]
}

export function validateComponentIO(
  componentType: string,
  inputs: Record<string, unknown>,
  config: Record<string, unknown>
): { valid: boolean; errors: string[] } {
  const spec = getComponentSpec(componentType)
  if (!spec) {
    return { valid: false, errors: [`Unknown component type: ${componentType}`] }
  }

  const errors: string[] = []

  // Validate required inputs
  spec.inputs.filter(i => i.required).forEach(input => {
    if (!(input.name in inputs)) {
      errors.push(`Missing required input: ${input.name}`)
    }
  })

  // Validate config types
  spec.config.forEach(configItem => {
    if (configItem.name in config) {
      const value = config[configItem.name]
      const expectedType = configItem.type === 'select' || configItem.type === 'multiselect'
        ? 'string'
        : configItem.type

      if (typeof value !== expectedType && expectedType !== 'number') {
        errors.push(`Config '${configItem.name}' should be of type ${expectedType}`)
      }
    }
  })

  return { valid: errors.length === 0, errors }
}
