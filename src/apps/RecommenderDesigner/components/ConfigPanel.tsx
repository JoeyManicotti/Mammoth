import { useState, useEffect } from 'react'
import { ComponentData } from '../types'
import { getComponentSpec, ComponentSpec } from '../componentSpecs'
import './ConfigPanel.css'

interface ConfigPanelProps {
  component: ComponentData | null
  onUpdateConfig: (componentId: string, config: Record<string, unknown>) => void
  onClose: () => void
}

const ConfigPanel = ({ component, onUpdateConfig, onClose }: ConfigPanelProps) => {
  const [config, setConfig] = useState<Record<string, unknown>>({})
  const [spec, setSpec] = useState<ComponentSpec | null>(null)

  useEffect(() => {
    if (component) {
      const componentSpec = getComponentSpec(component.type)
      setSpec(componentSpec || null)

      // Initialize config with defaults
      if (componentSpec) {
        const defaultConfig: Record<string, unknown> = {}
        componentSpec.config.forEach(item => {
          defaultConfig[item.name] = component.config?.[item.name] ?? item.default
        })
        setConfig(defaultConfig)
      }
    }
  }, [component])

  if (!component || !spec) {
    return null
  }

  const handleChange = (name: string, value: unknown) => {
    const newConfig = { ...config, [name]: value }
    setConfig(newConfig)
  }

  const handleSave = () => {
    onUpdateConfig(component.id, config)
    onClose()
  }

  const renderConfigInput = (configItem: ComponentSpec['config'][0]) => {
    const value = config[configItem.name]

    switch (configItem.type) {
      case 'string':
        return (
          <input
            type="text"
            value={value as string}
            onChange={(e) => handleChange(configItem.name, e.target.value)}
            className="config-input"
          />
        )

      case 'number':
        return (
          <input
            type="number"
            value={value as number}
            onChange={(e) => handleChange(configItem.name, parseFloat(e.target.value))}
            className="config-input"
            step="any"
          />
        )

      case 'boolean':
        return (
          <label className="config-checkbox">
            <input
              type="checkbox"
              checked={value as boolean}
              onChange={(e) => handleChange(configItem.name, e.target.checked)}
            />
            <span className="checkbox-label">Enabled</span>
          </label>
        )

      case 'select':
        return (
          <select
            value={value as string}
            onChange={(e) => handleChange(configItem.name, e.target.value)}
            className="config-select"
          >
            {configItem.options?.map(option => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        )

      case 'multiselect':
        const currentValues = (value as string[]) || []
        return (
          <div className="config-multiselect">
            {configItem.options?.map(option => (
              <label key={option} className="config-checkbox">
                <input
                  type="checkbox"
                  checked={currentValues.includes(option)}
                  onChange={(e) => {
                    const newValues = e.target.checked
                      ? [...currentValues, option]
                      : currentValues.filter(v => v !== option)
                    handleChange(configItem.name, newValues)
                  }}
                />
                <span className="checkbox-label">{option}</span>
              </label>
            ))}
          </div>
        )

      default:
        return <div>Unsupported type: {configItem.type}</div>
    }
  }

  return (
    <div className="config-panel-overlay" onClick={onClose}>
      <div className="config-panel" onClick={(e) => e.stopPropagation()}>
        <div className="config-panel-header">
          <div>
            <h2>{spec.name} Configuration</h2>
            <p className="config-description">{spec.description}</p>
          </div>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        <div className="config-panel-content">
          {/* Component Information */}
          <section className="config-section">
            <h3>Component Information</h3>
            <div className="info-grid">
              <div className="info-item">
                <span className="info-label">Type:</span>
                <span className="info-value">{spec.type}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Category:</span>
                <span className="info-value">{spec.category}</span>
              </div>
            </div>
          </section>

          {/* Inputs */}
          {spec.inputs.length > 0 && (
            <section className="config-section">
              <h3>Inputs</h3>
              {spec.inputs.map(input => (
                <div key={input.name} className="io-item">
                  <div className="io-header">
                    <span className="io-name">{input.name}</span>
                    <span className={`io-badge ${input.required ? 'required' : 'optional'}`}>
                      {input.required ? 'Required' : 'Optional'}
                    </span>
                  </div>
                  <div className="io-details">
                    <span className="io-type">{input.type}</span>
                    <span className="io-description">{input.description}</span>
                  </div>
                </div>
              ))}
            </section>
          )}

          {/* Outputs */}
          {spec.outputs.length > 0 && (
            <section className="config-section">
              <h3>Outputs</h3>
              {spec.outputs.map(output => (
                <div key={output.name} className="io-item">
                  <div className="io-header">
                    <span className="io-name">{output.name}</span>
                    <span className={`io-badge ${output.required ? 'required' : 'optional'}`}>
                      {output.required ? 'Required' : 'Optional'}
                    </span>
                  </div>
                  <div className="io-details">
                    <span className="io-type">{output.type}</span>
                    <span className="io-description">{output.description}</span>
                  </div>
                </div>
              ))}
            </section>
          )}

          {/* Configuration */}
          {spec.config.length > 0 && (
            <section className="config-section">
              <h3>Configuration</h3>
              {spec.config.map(configItem => (
                <div key={configItem.name} className="config-item">
                  <label className="config-label">
                    {configItem.name}
                    <span className="config-item-description">{configItem.description}</span>
                  </label>
                  {renderConfigInput(configItem)}
                </div>
              ))}
            </section>
          )}

          {/* Test Cases */}
          {spec.testCases.length > 0 && (
            <section className="config-section">
              <h3>Test Cases</h3>
              {spec.testCases.map((testCase, idx) => (
                <details key={idx} className="test-case">
                  <summary className="test-case-summary">{testCase.name}</summary>
                  <div className="test-case-content">
                    <p className="test-case-description">{testCase.description}</p>
                    <div className="test-case-details">
                      <div>
                        <strong>Config:</strong>
                        <pre>{JSON.stringify(testCase.config, null, 2)}</pre>
                      </div>
                      <div>
                        <strong>Expected Output:</strong>
                        <pre>{JSON.stringify(testCase.expectedOutput, null, 2)}</pre>
                      </div>
                    </div>
                  </div>
                </details>
              ))}
            </section>
          )}
        </div>

        <div className="config-panel-footer">
          <button className="config-button cancel" onClick={onClose}>
            Cancel
          </button>
          <button className="config-button save" onClick={handleSave}>
            Save Configuration
          </button>
        </div>
      </div>
    </div>
  )
}

export default ConfigPanel
