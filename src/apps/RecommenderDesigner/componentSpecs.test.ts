import { describe, it, expect } from 'vitest'
import {
  COMPONENT_SPECIFICATIONS,
  getComponentSpec,
  validateComponentIO,
  type ComponentSpec
} from './componentSpecs'

describe('ComponentSpecs', () => {
  describe('Specification Definitions', () => {
    it('should have specifications for core components', () => {
      expect(COMPONENT_SPECIFICATIONS['data-source']).toBeDefined()
      expect(COMPONENT_SPECIFICATIONS['user-profile']).toBeDefined()
      expect(COMPONENT_SPECIFICATIONS['item-catalog']).toBeDefined()
      expect(COMPONENT_SPECIFICATIONS['collaborative-filter']).toBeDefined()
      expect(COMPONENT_SPECIFICATIONS['matrix-factorization']).toBeDefined()
      expect(COMPONENT_SPECIFICATIONS['deep-learning']).toBeDefined()
      expect(COMPONENT_SPECIFICATIONS['evaluation']).toBeDefined()
    })

    it('all specs should have required fields', () => {
      Object.values(COMPONENT_SPECIFICATIONS).forEach((spec: ComponentSpec) => {
        expect(spec.type).toBeTruthy()
        expect(spec.name).toBeTruthy()
        expect(spec.category).toBeTruthy()
        expect(spec.description).toBeTruthy()
        expect(spec.inputs).toBeDefined()
        expect(spec.outputs).toBeDefined()
        expect(spec.config).toBeDefined()
        expect(spec.testCases).toBeDefined()
      })
    })

    it('all specs should have at least one test case', () => {
      Object.values(COMPONENT_SPECIFICATIONS).forEach((spec: ComponentSpec) => {
        expect(spec.testCases.length).toBeGreaterThan(0)
      })
    })
  })

  describe('Data Source Component', () => {
    const spec = COMPONENT_SPECIFICATIONS['data-source']

    it('should have correct configuration', () => {
      expect(spec.type).toBe('data-source')
      expect(spec.name).toBe('Data Source')
      expect(spec.category).toBe('data')
    })

    it('should have no inputs', () => {
      expect(spec.inputs).toHaveLength(0)
    })

    it('should output dataframe', () => {
      expect(spec.outputs).toHaveLength(1)
      expect(spec.outputs[0].type).toBe('dataframe')
      expect(spec.outputs[0].required).toBe(true)
    })

    it('should have data source configuration options', () => {
      const dataSourceConfig = spec.config.find(c => c.name === 'dataSource')
      expect(dataSourceConfig).toBeDefined()
      expect(dataSourceConfig?.type).toBe('select')
      expect(dataSourceConfig?.options).toContain('csv')
      expect(dataSourceConfig?.options).toContain('synthetic')
    })

    it('should have test case for MovieLens 100K', () => {
      const mlTest = spec.testCases.find(t => t.name === 'Load MovieLens 100K')
      expect(mlTest).toBeDefined()
      expect(mlTest?.config.dataSource).toBe('csv')
    })

    it('should have test case for synthetic data', () => {
      const syntheticTest = spec.testCases.find(t => t.name === 'Generate synthetic data')
      expect(syntheticTest).toBeDefined()
      expect(syntheticTest?.config.dataSource).toBe('synthetic')
    })
  })

  describe('Collaborative Filter Component', () => {
    const spec = COMPONENT_SPECIFICATIONS['collaborative-filter']

    it('should accept interaction matrix', () => {
      expect(spec.inputs).toHaveLength(1)
      expect(spec.inputs[0].type).toBe('matrix')
      expect(spec.inputs[0].required).toBe(true)
    })

    it('should output predictions', () => {
      const predOutput = spec.outputs.find(o => o.name === 'predictions')
      expect(predOutput).toBeDefined()
      expect(predOutput?.type).toBe('matrix')
      expect(predOutput?.required).toBe(true)
    })

    it('should have method configuration', () => {
      const methodConfig = spec.config.find(c => c.name === 'method')
      expect(methodConfig).toBeDefined()
      expect(methodConfig?.options).toContain('user-based')
      expect(methodConfig?.options).toContain('item-based')
    })

    it('should have similarity metric options', () => {
      const similarityConfig = spec.config.find(c => c.name === 'similarity')
      expect(similarityConfig).toBeDefined()
      expect(similarityConfig?.options).toContain('cosine')
      expect(similarityConfig?.options).toContain('pearson')
      expect(similarityConfig?.options).toContain('jaccard')
    })

    it('should have k_neighbors parameter', () => {
      const kConfig = spec.config.find(c => c.name === 'k_neighbors')
      expect(kConfig).toBeDefined()
      expect(kConfig?.type).toBe('number')
      expect(kConfig?.default).toBe(50)
    })
  })

  describe('Matrix Factorization Component', () => {
    const spec = COMPONENT_SPECIFICATIONS['matrix-factorization']

    it('should have factorization method options', () => {
      const methodConfig = spec.config.find(c => c.name === 'method')
      expect(methodConfig).toBeDefined()
      expect(methodConfig?.options).toContain('svd')
      expect(methodConfig?.options).toContain('als')
      expect(methodConfig?.options).toContain('nmf')
    })

    it('should have hyperparameter configurations', () => {
      const nFactors = spec.config.find(c => c.name === 'n_factors')
      const nEpochs = spec.config.find(c => c.name === 'n_epochs')
      const lr = spec.config.find(c => c.name === 'learning_rate')
      const reg = spec.config.find(c => c.name === 'regularization')

      expect(nFactors).toBeDefined()
      expect(nEpochs).toBeDefined()
      expect(lr).toBeDefined()
      expect(reg).toBeDefined()
    })

    it('should output user and item factors', () => {
      const userFactors = spec.outputs.find(o => o.name === 'userFactors')
      const itemFactors = spec.outputs.find(o => o.name === 'itemFactors')

      expect(userFactors).toBeDefined()
      expect(itemFactors).toBeDefined()
      expect(userFactors?.type).toBe('matrix')
      expect(itemFactors?.type).toBe('matrix')
    })

    it('should have SVD test case', () => {
      const svdTest = spec.testCases.find(t => t.name === 'SVD on MovieLens')
      expect(svdTest).toBeDefined()
      expect(svdTest?.config.method).toBe('svd')
      expect(svdTest?.config.n_factors).toBe(100)
    })
  })

  describe('Deep Learning Component', () => {
    const spec = COMPONENT_SPECIFICATIONS['deep-learning']

    it('should require user and item features', () => {
      expect(spec.inputs.length).toBeGreaterThanOrEqual(2)
      const userFeatures = spec.inputs.find(i => i.name === 'userFeatures')
      const itemFeatures = spec.inputs.find(i => i.name === 'itemFeatures')

      expect(userFeatures).toBeDefined()
      expect(itemFeatures).toBeDefined()
      expect(userFeatures?.required).toBe(true)
      expect(itemFeatures?.required).toBe(true)
    })

    it('should have architecture options', () => {
      const archConfig = spec.config.find(c => c.name === 'architecture')
      expect(archConfig).toBeDefined()
      expect(archConfig?.options).toContain('ncf')
      expect(archConfig?.options).toContain('wide_deep')
      expect(archConfig?.options).toContain('deepfm')
    })

    it('should have neural network hyperparameters', () => {
      const embDim = spec.config.find(c => c.name === 'embedding_dim')
      const hiddenLayers = spec.config.find(c => c.name === 'hidden_layers')
      const dropout = spec.config.find(c => c.name === 'dropout')
      const batchSize = spec.config.find(c => c.name === 'batch_size')
      const epochs = spec.config.find(c => c.name === 'epochs')

      expect(embDim).toBeDefined()
      expect(hiddenLayers).toBeDefined()
      expect(dropout).toBeDefined()
      expect(batchSize).toBeDefined()
      expect(epochs).toBeDefined()
    })

    it('should output trained model', () => {
      const modelOutput = spec.outputs.find(o => o.name === 'model')
      expect(modelOutput).toBeDefined()
      expect(modelOutput?.type).toBe('model')
      expect(modelOutput?.required).toBe(true)
    })
  })

  describe('Evaluation Component', () => {
    const spec = COMPONENT_SPECIFICATIONS['evaluation']

    it('should accept predictions and ground truth', () => {
      expect(spec.inputs.length).toBeGreaterThanOrEqual(2)
      const predictions = spec.inputs.find(i => i.name === 'predictions')
      const groundTruth = spec.inputs.find(i => i.name === 'groundTruth')

      expect(predictions).toBeDefined()
      expect(groundTruth).toBeDefined()
      expect(predictions?.required).toBe(true)
      expect(groundTruth?.required).toBe(true)
    })

    it('should support multiple metrics', () => {
      const metricsConfig = spec.config.find(c => c.name === 'metrics')
      expect(metricsConfig).toBeDefined()
      expect(metricsConfig?.type).toBe('multiselect')
      expect(metricsConfig?.options).toContain('rmse')
      expect(metricsConfig?.options).toContain('precision')
      expect(metricsConfig?.options).toContain('recall')
      expect(metricsConfig?.options).toContain('ndcg')
    })

    it('should output metrics', () => {
      expect(spec.outputs).toHaveLength(1)
      expect(spec.outputs[0].type).toBe('metrics')
      expect(spec.outputs[0].required).toBe(true)
    })

    it('should have comprehensive evaluation test case', () => {
      const evalTest = spec.testCases.find(t => t.name === 'Comprehensive evaluation')
      expect(evalTest).toBeDefined()
      expect(evalTest?.config.metrics).toContain('rmse')
      expect(evalTest?.config.metrics).toContain('precision')
    })
  })

  describe('Helper Functions', () => {
    it('getComponentSpec should return spec for valid type', () => {
      const spec = getComponentSpec('data-source')
      expect(spec).toBeDefined()
      expect(spec?.type).toBe('data-source')
    })

    it('getComponentSpec should return undefined for invalid type', () => {
      const spec = getComponentSpec('invalid-component')
      expect(spec).toBeUndefined()
    })
  })

  describe('Input/Output Validation', () => {
    it('should validate data-source with correct config', () => {
      const result = validateComponentIO('data-source', {}, {
        dataSource: 'csv',
        filePath: 'test.csv',
        sampleSize: 1000
      })
      expect(result.valid).toBe(true)
      expect(result.errors).toHaveLength(0)
    })

    it('should fail validation for unknown component', () => {
      const result = validateComponentIO('unknown-component', {}, {})
      expect(result.valid).toBe(false)
      expect(result.errors.length).toBeGreaterThan(0)
    })

    it('should fail validation for missing required inputs', () => {
      const result = validateComponentIO('collaborative-filter', {}, {})
      expect(result.valid).toBe(false)
      expect(result.errors).toContain('Missing required input: interactionMatrix')
    })

    it('should validate deep-learning with all required inputs', () => {
      const result = validateComponentIO('deep-learning', {
        userFeatures: {},
        itemFeatures: {},
        interactions: {}
      }, {
        architecture: 'ncf',
        embedding_dim: 64
      })
      expect(result.valid).toBe(true)
    })
  })

  describe('Test Case Completeness', () => {
    it('all test cases should have required fields', () => {
      Object.values(COMPONENT_SPECIFICATIONS).forEach((spec: ComponentSpec) => {
        spec.testCases.forEach(testCase => {
          expect(testCase.name).toBeTruthy()
          expect(testCase.description).toBeTruthy()
          expect(testCase.input).toBeDefined()
          expect(testCase.config).toBeDefined()
          expect(testCase.expectedOutput).toBeDefined()
        })
      })
    })

    it('test cases should cover different configurations', () => {
      const mfSpec = COMPONENT_SPECIFICATIONS['matrix-factorization']
      expect(mfSpec.testCases.length).toBeGreaterThan(0)

      const cfSpec = COMPONENT_SPECIFICATIONS['collaborative-filter']
      expect(cfSpec.testCases.length).toBeGreaterThan(0)
    })
  })

  describe('Configuration Type Safety', () => {
    it('all config items should have valid types', () => {
      const validTypes = ['string', 'number', 'boolean', 'select', 'multiselect']

      Object.values(COMPONENT_SPECIFICATIONS).forEach((spec: ComponentSpec) => {
        spec.config.forEach(configItem => {
          expect(validTypes).toContain(configItem.type)
          expect(configItem.default).toBeDefined()
          expect(configItem.description).toBeTruthy()
        })
      })
    })

    it('select and multiselect configs should have options', () => {
      Object.values(COMPONENT_SPECIFICATIONS).forEach((spec: ComponentSpec) => {
        spec.config.forEach(configItem => {
          if (configItem.type === 'select' || configItem.type === 'multiselect') {
            expect(configItem.options).toBeDefined()
            expect(configItem.options!.length).toBeGreaterThan(0)
          }
        })
      })
    })
  })
})
