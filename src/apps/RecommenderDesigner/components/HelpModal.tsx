import './HelpModal.css'

interface HelpModalProps {
  onClose: () => void
}

const HelpModal = ({ onClose }: HelpModalProps) => {
  return (
    <div className="help-modal-overlay" onClick={onClose}>
      <div className="help-modal" onClick={(e) => e.stopPropagation()}>
        <div className="help-modal-header">
          <h2>🎓 Mammoth Recommender Designer Help</h2>
          <button className="help-modal-close" onClick={onClose}>×</button>
        </div>

        <div className="help-modal-content">
          <section className="help-section">
            <h3>📝 Getting Started</h3>
            <ul>
              <li>Drag components from the left palette onto the canvas</li>
              <li>Components are color-coded by category:
                <ul>
                  <li><span className="color-tag input">Blue</span> - Input (Data Source, Features)</li>
                  <li><span className="color-tag transform">Purple</span> - Transform (Split, Preprocessor)</li>
                  <li><span className="color-tag model">Amber</span> - Model (XGBoost, Random Forest, etc.)</li>
                  <li><span className="color-tag output">Green</span> - Output (Predictions, Evaluation)</li>
                </ul>
              </li>
            </ul>
          </section>

          <section className="help-section">
            <h3>🔗 Connecting Components</h3>
            <ul>
              <li><strong>Method 1:</strong> Click a connection point (circles on component edges), then click another component's connection point</li>
              <li><strong>Method 2:</strong> Right-click a component → "Connect" → click the target component</li>
              <li>Components glow when in connection mode</li>
              <li>Only valid connections are allowed (e.g., Data Source → Train/Test Split → Model)</li>
              <li>Click the × button on a connection line to delete it</li>
            </ul>
          </section>

          <section className="help-section">
            <h3>🎨 Canvas Controls</h3>
            <ul>
              <li><strong>Zoom:</strong> Mouse wheel or toolbar buttons (+/-)</li>
              <li><strong>Pan:</strong> Shift + Drag or Middle mouse button + Drag</li>
              <li><strong>Reset View:</strong> Click "100%" in toolbar</li>
              <li><strong>Move Component:</strong> Click and drag</li>
              <li><strong>Select Component:</strong> Click once</li>
              <li><strong>Configure Component:</strong> Double-click or right-click → "Configure"</li>
            </ul>
          </section>

          <section className="help-section">
            <h3>💾 Save & Load</h3>
            <ul>
              <li><strong>Auto-save:</strong> Your canvas is automatically saved to browser storage</li>
              <li><strong>Export:</strong> Click "Save" to download your workflow as a JSON file</li>
              <li><strong>Import:</strong> Click "Load" to import a previously saved workflow</li>
              <li>Workflows persist when navigating between pages</li>
            </ul>
          </section>

          <section className="help-section">
            <h3>📊 Example Workflows</h3>
            <p>Check the left panel for 5 pre-configured workflow templates:</p>
            <ol>
              <li>Simple Collaborative Filtering</li>
              <li>XGBoost with Features</li>
              <li>Matrix Factorization Pipeline</li>
              <li>Deep Learning Pipeline</li>
              <li>Model Comparison</li>
            </ol>
          </section>

          <section className="help-section">
            <h3>⌨️ Keyboard Shortcuts</h3>
            <ul>
              <li><kbd>Delete</kbd> or <kbd>Backspace</kbd> - Delete selected component</li>
              <li><kbd>Esc</kbd> - Cancel connection mode</li>
              <li><kbd>Shift + Drag</kbd> - Pan canvas</li>
            </ul>
          </section>
        </div>

        <div className="help-modal-footer">
          <button className="help-modal-button" onClick={onClose}>Got it!</button>
        </div>
      </div>
    </div>
  )
}

export default HelpModal
