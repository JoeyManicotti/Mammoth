/**
 * API Service for Backend Communication
 *
 * Provides methods for interacting with the Mammoth backend API
 */

const API_BASE_URL = 'http://localhost:5000'

export interface DataLoadRequest {
  source: 'movielens-100k' | 'synthetic'
  sample_size?: number
  train_test_split?: number
}

export interface DataLoadResponse {
  success: boolean
  pipeline_id: string
  metadata: {
    n_users: number
    n_items: number
    n_interactions: number
    sparsity: number
  }
  train_size: number
  test_size: number
  error?: string
}

export interface ModelTrainRequest {
  pipeline_id: string
  model_type: 'xgboost' | 'random_forest' | 'matrix_factorization' | 'collaborative_filtering'
  config: Record<string, unknown>
}

export interface ModelTrainResponse {
  success: boolean
  pipeline_id: string
  model_type: string
  training_history: Record<string, unknown>
  error?: string
}

export interface PredictRequest {
  pipeline_id: string
  user_ids: number[]
  top_k?: number
}

export interface PredictResponse {
  success: boolean
  predictions: Record<number, Array<[number, number]>>
  error?: string
}

export interface EvaluateRequest {
  pipeline_id: string
  metrics: string[]
  k_values?: number[]
}

export interface EvaluateResponse {
  success: boolean
  metrics: Record<string, number>
  error?: string
}

export interface CompareRequest {
  pipeline_id: string
  model_configs: Array<{
    type: string
    config: Record<string, unknown>
  }>
  metrics: string[]
}

export interface CompareResponse {
  success: boolean
  comparison: Array<{
    model_type: string
    config: Record<string, unknown>
    metrics: Record<string, number>
  }>
  error?: string
}

export interface PipelineInfo {
  pipeline_id: string
  metadata: Record<string, unknown>
  has_model: boolean
  model_type?: string
  has_evaluation: boolean
  evaluation: Record<string, number>
}

class ApiService {
  private baseUrl: string

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`

    const defaultOptions: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
      },
      ...options,
    }

    try {
      const response = await fetch(url, defaultOptions)

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error)
      throw error
    }
  }

  async healthCheck(): Promise<{ status: string; service: string }> {
    return this.request('/health')
  }

  async loadData(request: DataLoadRequest): Promise<DataLoadResponse> {
    return this.request('/api/data/load', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  }

  async trainModel(request: ModelTrainRequest): Promise<ModelTrainResponse> {
    return this.request('/api/models/train', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  }

  async predict(request: PredictRequest): Promise<PredictResponse> {
    return this.request('/api/models/predict', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  }

  async evaluate(request: EvaluateRequest): Promise<EvaluateResponse> {
    return this.request('/api/models/evaluate', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  }

  async compareModels(request: CompareRequest): Promise<CompareResponse> {
    return this.request('/api/models/compare', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  }

  async getPipelineInfo(pipelineId: string): Promise<{ success: boolean; info: PipelineInfo }> {
    return this.request(`/api/pipeline/info/${pipelineId}`)
  }
}

// Export singleton instance
export const apiService = new ApiService()

// Export class for testing or custom instances
export default ApiService
