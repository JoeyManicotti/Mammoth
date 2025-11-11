export interface Position {
  x: number
  y: number
}

export interface ComponentData {
  id: string
  type: ComponentType
  position: Position
  label: string
  config?: Record<string, unknown>
}

export interface Connection {
  id: string
  from: string
  to: string
}

export type ComponentType =
  | 'data-source'
  | 'feature-extraction'
  | 'user-profile'
  | 'item-catalog'
  | 'collaborative-filter'
  | 'content-filter'
  | 'matrix-factorization'
  | 'deep-learning'
  | 'ranking'
  | 'output'
  | 'evaluation'

export interface ComponentDefinition {
  type: ComponentType
  label: string
  icon: string
  category: 'data' | 'processing' | 'algorithm' | 'output'
  description: string
}
