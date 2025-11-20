import { describe, it, expect } from 'vitest'
import {
  SIMPLIFIED_COMPONENTS,
  EXAMPLE_WORKFLOWS,
  isValidConnection,
  getSimplifiedComponent,
  getComponentsByCategory,
  getComponentColor,
  COLOR_PALETTE
} from './simplifiedComponents'

describe('SimplifiedComponents', () => {
  describe('Component Definitions', () => {
    it('should have all 11 essential components defined', () => {
      expect(SIMPLIFIED_COMPONENTS).toHaveLength(11)
    })

    it('should have unique component types', () => {
      const types = SIMPLIFIED_COMPONENTS.map(c => c.type)
      const uniqueTypes = new Set(types)
      expect(uniqueTypes.size).toBe(types.length)
    })

    it('should have valid categories for all components', () => {
      const validCategories = ['input', 'transform', 'model', 'output']
      SIMPLIFIED_COMPONENTS.forEach(component => {
        expect(validCategories).toContain(component.category)
      })
    })

    it('should have non-empty labels and descriptions', () => {
      SIMPLIFIED_COMPONENTS.forEach(component => {
        expect(component.label).toBeTruthy()
        expect(component.description).toBeTruthy()
        expect(component.icon).toBeTruthy()
      })
    })
  })

  describe('Input Blocks', () => {
    const inputBlocks = SIMPLIFIED_COMPONENTS.filter(c => c.category === 'input')

    it('should have 2 input blocks', () => {
      expect(inputBlocks).toHaveLength(2)
    })

    it('should include data-source component', () => {
      const dataSource = inputBlocks.find(c => c.type === 'data-source')
      expect(dataSource).toBeDefined()
      expect(dataSource?.label).toBe('Data Source')
      expect(dataSource?.produces).toBe('dataframe')
      expect(dataSource?.accepts).toHaveLength(0)
    })

    it('should include features-input component', () => {
      const featuresInput = inputBlocks.find(c => c.type === 'features-input')
      expect(featuresInput).toBeDefined()
      expect(featuresInput?.label).toBe('Features')
      expect(featuresInput?.produces).toBe('features')
      expect(featuresInput?.accepts).toHaveLength(0)
    })

    it('input blocks should accept no inputs', () => {
      inputBlocks.forEach(block => {
        expect(block.accepts).toHaveLength(0)
      })
    })
  })

  describe('Transform Blocks', () => {
    const transformBlocks = SIMPLIFIED_COMPONENTS.filter(c => c.category === 'transform')

    it('should have 2 transform blocks', () => {
      expect(transformBlocks).toHaveLength(2)
    })

    it('should include split component', () => {
      const split = transformBlocks.find(c => c.type === 'split')
      expect(split).toBeDefined()
      expect(split?.accepts).toContain('dataframe')
      expect(split?.produces).toBe('split-data')
    })

    it('should include preprocessor component', () => {
      const preprocessor = transformBlocks.find(c => c.type === 'preprocessor')
      expect(preprocessor).toBeDefined()
      expect(preprocessor?.accepts).toContain('dataframe')
      expect(preprocessor?.accepts).toContain('features')
      expect(preprocessor?.produces).toBe('processed-data')
    })
  })

  describe('Model Blocks', () => {
    const modelBlocks = SIMPLIFIED_COMPONENTS.filter(c => c.category === 'model')

    it('should have 5 model blocks', () => {
      expect(modelBlocks).toHaveLength(5)
    })

    it('all model blocks should produce model output', () => {
      modelBlocks.forEach(block => {
        expect(block.produces).toBe('model')
      })
    })

    it('should include collaborative-filtering', () => {
      const cf = modelBlocks.find(c => c.type === 'collaborative-filtering')
      expect(cf).toBeDefined()
      expect(cf?.label).toBe('Collaborative Filter')
    })

    it('should include matrix-factorization', () => {
      const mf = modelBlocks.find(c => c.type === 'matrix-factorization')
      expect(mf).toBeDefined()
      expect(mf?.label).toBe('Matrix Factorization')
    })

    it('should include xgboost', () => {
      const xgb = modelBlocks.find(c => c.type === 'xgboost')
      expect(xgb).toBeDefined()
      expect(xgb?.accepts).toContain('features')
    })

    it('should include random-forest', () => {
      const rf = modelBlocks.find(c => c.type === 'random-forest')
      expect(rf).toBeDefined()
      expect(rf?.accepts).toContain('features')
    })

    it('should include deep-learning', () => {
      const dl = modelBlocks.find(c => c.type === 'deep-learning')
      expect(dl).toBeDefined()
      expect(dl?.label).toBe('Neural Network')
    })
  })

  describe('Output Blocks', () => {
    const outputBlocks = SIMPLIFIED_COMPONENTS.filter(c => c.category === 'output')

    it('should have 2 output blocks', () => {
      expect(outputBlocks).toHaveLength(2)
    })

    it('should include predictions component', () => {
      const predictions = outputBlocks.find(c => c.type === 'predictions')
      expect(predictions).toBeDefined()
      expect(predictions?.accepts).toContain('model')
      expect(predictions?.produces).toBe('recommendations')
    })

    it('should include evaluation component', () => {
      const evaluation = outputBlocks.find(c => c.type === 'evaluation')
      expect(evaluation).toBeDefined()
      expect(evaluation?.accepts).toContain('model')
      expect(evaluation?.produces).toBe('metrics')
    })
  })

  describe('Connection Validation', () => {
    it('should allow data-source to connect to split', () => {
      expect(isValidConnection('data-source', 'split')).toBe(true)
    })

    it('should allow split to connect to collaborative-filtering', () => {
      expect(isValidConnection('split', 'collaborative-filtering')).toBe(true)
    })

    it('should allow model to connect to predictions', () => {
      expect(isValidConnection('collaborative-filtering', 'predictions')).toBe(true)
    })

    it('should allow model to connect to evaluation', () => {
      expect(isValidConnection('matrix-factorization', 'evaluation')).toBe(true)
    })

    it('should not allow predictions to connect to data-source', () => {
      expect(isValidConnection('predictions', 'data-source')).toBe(false)
    })

    it('should not allow invalid type connections', () => {
      expect(isValidConnection('data-source', 'predictions')).toBe(false)
    })

    it('should return false for non-existent components', () => {
      expect(isValidConnection('invalid-type', 'split')).toBe(false)
      expect(isValidConnection('split', 'invalid-type')).toBe(false)
    })

    it('should allow features-input to xgboost', () => {
      expect(isValidConnection('features-input', 'xgboost')).toBe(true)
    })
  })

  describe('Example Workflows', () => {
    it('should have 5 example workflows', () => {
      expect(EXAMPLE_WORKFLOWS).toHaveLength(5)
    })

    it('all workflows should have valid component types', () => {
      EXAMPLE_WORKFLOWS.forEach(workflow => {
        workflow.blocks.forEach(blockType => {
          const component = SIMPLIFIED_COMPONENTS.find(c => c.type === blockType)
          expect(component).toBeDefined()
        })
      })
    })

    it('Simple Collaborative Filtering workflow should be valid', () => {
      const workflow = EXAMPLE_WORKFLOWS.find(w => w.name === 'Simple Collaborative Filtering')
      expect(workflow).toBeDefined()
      expect(workflow?.blocks).toEqual([
        'data-source',
        'split',
        'collaborative-filtering',
        'predictions',
        'evaluation'
      ])
    })

    it('XGBoost with Features workflow should include features-input', () => {
      const workflow = EXAMPLE_WORKFLOWS.find(w => w.name === 'XGBoost with Features')
      expect(workflow).toBeDefined()
      expect(workflow?.blocks).toContain('features-input')
      expect(workflow?.blocks).toContain('xgboost')
    })

    it('Model Comparison workflow should have multiple models', () => {
      const workflow = EXAMPLE_WORKFLOWS.find(w => w.name === 'Model Comparison')
      expect(workflow).toBeDefined()
      const models = workflow?.blocks.filter(b => {
        const comp = SIMPLIFIED_COMPONENTS.find(c => c.type === b)
        return comp?.category === 'model'
      })
      expect(models?.length).toBeGreaterThan(1)
    })
  })

  describe('Helper Functions', () => {
    it('getSimplifiedComponent should return component by type', () => {
      const component = getSimplifiedComponent('data-source')
      expect(component).toBeDefined()
      expect(component?.type).toBe('data-source')
    })

    it('getSimplifiedComponent should return undefined for invalid type', () => {
      const component = getSimplifiedComponent('invalid-type')
      expect(component).toBeUndefined()
    })

    it('getComponentsByCategory should return all input components', () => {
      const inputComponents = getComponentsByCategory('input')
      expect(inputComponents).toHaveLength(2)
      inputComponents.forEach(c => {
        expect(c.category).toBe('input')
      })
    })

    it('getComponentsByCategory should return all model components', () => {
      const modelComponents = getComponentsByCategory('model')
      expect(modelComponents).toHaveLength(5)
    })

    it('getComponentColor should return correct colors', () => {
      expect(getComponentColor('input')).toEqual(COLOR_PALETTE.input)
      expect(getComponentColor('transform')).toEqual(COLOR_PALETTE.transform)
      expect(getComponentColor('model')).toEqual(COLOR_PALETTE.model)
      expect(getComponentColor('output')).toEqual(COLOR_PALETTE.output)
    })

    it('getComponentColor should return default for invalid category', () => {
      expect(getComponentColor('invalid')).toEqual(COLOR_PALETTE.transform)
    })
  })

  describe('Color Palette', () => {
    it('should have colors for all categories', () => {
      expect(COLOR_PALETTE.input).toBeDefined()
      expect(COLOR_PALETTE.transform).toBeDefined()
      expect(COLOR_PALETTE.model).toBeDefined()
      expect(COLOR_PALETTE.output).toBeDefined()
    })

    it('all color palettes should have required properties', () => {
      Object.values(COLOR_PALETTE).forEach(palette => {
        expect(palette.primary).toBeDefined()
        expect(palette.secondary).toBeDefined()
        expect(palette.gradient).toBeDefined()
        expect(palette.border).toBeDefined()
        expect(palette.text).toBeDefined()
      })
    })
  })

  describe('Data Flow Validation', () => {
    it('should create valid pipeline: data -> split -> model -> output', () => {
      expect(isValidConnection('data-source', 'split')).toBe(true)
      expect(isValidConnection('split', 'collaborative-filtering')).toBe(true)
      expect(isValidConnection('collaborative-filtering', 'predictions')).toBe(true)
    })

    it('should create valid pipeline with preprocessing', () => {
      expect(isValidConnection('data-source', 'preprocessor')).toBe(true)
      expect(isValidConnection('preprocessor', 'xgboost')).toBe(true)
      expect(isValidConnection('xgboost', 'evaluation')).toBe(true)
    })

    it('should support parallel model training', () => {
      expect(isValidConnection('split', 'collaborative-filtering')).toBe(true)
      expect(isValidConnection('split', 'matrix-factorization')).toBe(true)
      expect(isValidConnection('split', 'xgboost')).toBe(true)
    })
  })
})
