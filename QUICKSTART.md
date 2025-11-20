# Mammoth Quick Start Guide

Get started with Mammoth Recommender Designer in minutes!

---

## Installation

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- Git

### Setup

```bash
# Clone the repository
git clone https://github.com/JoeyManicotti/Mammoth.git
cd Mammoth

# Install frontend dependencies
npm install

# Install backend dependencies
cd backend
pip install -r requirements.txt
cd ..
```

---

## Running the Application

### Development Mode

**Frontend**:
```bash
npm run dev
```
Opens at http://localhost:5173

**Backend** (optional, for executing pipelines):
```bash
cd backend
python app.py
```
API runs at http://localhost:5000

### Production Build

```bash
npm run build
npm run preview
```

---

## Your First Workflow in 5 Minutes

### Step 1: Create a Simple Collaborative Filtering Pipeline

1. **Start the app**: `npm run dev`
2. **Open your browser**: Navigate to http://localhost:5173
3. **Drag components** from the left palette to the canvas:
   - Data Source (blue)
   - Train/Test Split (purple)
   - Collaborative Filter (amber)
   - Predictions (green)
   - Evaluation (green)

### Step 2: Connect Components

Click the connection point on each component and drag to the next:
```
Data Source → Split → Collaborative Filter → Predictions
                                          ↓
                                    Evaluation
```

### Step 3: Configure Components

Double-click each component to configure:

**Data Source**:
```json
{
  "dataSource": "synthetic",
  "n_users": 100,
  "n_items": 200,
  "n_interactions": 1000
}
```

**Split**:
```json
{
  "test_size": 0.2,
  "method": "random"
}
```

**Collaborative Filter**:
```json
{
  "method": "user-based",
  "k_neighbors": 50
}
```

**Predictions**:
```json
{
  "top_k": 10
}
```

**Evaluation**:
```json
{
  "metrics": ["rmse", "mae", "precision", "recall", "ndcg"]
}
```

### Step 4: Save Your Workflow

Click **Save** in the toolbar to download your pipeline as JSON.

---

## Running Backend Pipelines

### Python Example

```python
from backend.blocks import (
    DataSourceBlock,
    SplitBlock,
    CollaborativeFilteringBlock,
    PredictionsBlock,
    EvaluationBlock
)

# 1. Create and configure blocks
data = DataSourceBlock('data')
data.configure(
    data_source='synthetic',
    n_users=100,
    n_items=200,
    n_interactions=1000
)

split = SplitBlock('split')
split.configure(test_size=0.2)

model = CollaborativeFilteringBlock('cf')
model.configure(method='user-based')

predictions = PredictionsBlock('pred')
predictions.configure(top_k=10)

evaluation = EvaluationBlock('eval')
evaluation.configure(metrics=['rmse', 'precision', 'ndcg'])

# 2. Execute pipeline
data_out = data.execute({})
split_out = split.execute({'dataframe': data_out.data['dataframe']})
model_out = model.execute({'split-data': split_out.data['split-data']})
pred_out = predictions.execute({'model': model_out.data['model']})
eval_out = evaluation.execute({'model': model_out.data['model']})

# 3. View results
print("Recommendations:", pred_out.data['recommendations'])
print("Metrics:", eval_out.metrics)
```

### Output:
```
Recommendations: {0: [(45, 4.2), (78, 4.1), (12, 4.0), ...], ...}
Metrics: {'rmse': 0.95, 'precision@10': 0.32, 'ndcg@10': 0.35}
```

---

## Example Workflows

### 1. Matrix Factorization Pipeline

**Components**: Data Source → Split → Matrix Factorization → Evaluation

**Use Case**: SVD-based collaborative filtering

**Code**:
```python
from backend.blocks import DataSourceBlock, SplitBlock, MatrixFactorizationBlock, EvaluationBlock

data = DataSourceBlock('data')
data.configure(data_source='synthetic', n_users=200, n_items=300, n_interactions=2000)

split = SplitBlock('split')
split.configure(test_size=0.2)

mf = MatrixFactorizationBlock('mf')
mf.configure(method='svd', n_factors=50, n_epochs=20)

evaluation = EvaluationBlock('eval')
evaluation.configure(metrics=['rmse', 'mae'])

# Execute
data_out = data.execute({})
split_out = split.execute({'dataframe': data_out.data['dataframe']})
mf_out = mf.execute({'split-data': split_out.data['split-data']})
eval_out = evaluation.execute({'model': mf_out.data['model']})

print(f"RMSE: {eval_out.metrics['rmse']:.3f}")
print(f"MAE: {eval_out.metrics['mae']:.3f}")
```

### 2. Feature-Enhanced Model

**Components**: Data Source + Features → Preprocessor → Deep Learning → Predictions

**Use Case**: Neural network with user/item features

**Code**:
```python
from backend.blocks import (
    DataSourceBlock, FeaturesInputBlock, PreprocessorBlock,
    DeepLearningBlock, PredictionsBlock
)

# Load interaction data
data = DataSourceBlock('data')
data.configure(data_source='synthetic', n_users=100, n_items=150)

# Load features
user_features = FeaturesInputBlock('user_features')
user_features.configure(feature_type='user', n_entities=100)

item_features = FeaturesInputBlock('item_features')
item_features.configure(feature_type='item', n_entities=150)

# Preprocess
preprocessor = PreprocessorBlock('preproc')
preprocessor.configure(normalize=True, fill_missing=True)

# Train neural network
dl_model = DeepLearningBlock('neural_net')
dl_model.configure(
    architecture='ncf',
    embedding_dim=64,
    epochs=10
)

# Generate predictions
predictions = PredictionsBlock('predictions')
predictions.configure(top_k=20)

# Execute pipeline
data_out = data.execute({})
user_feat_out = user_features.execute({})
item_feat_out = item_features.execute({})
# ... continue execution
```

### 3. Model Comparison

**Components**: Data Source → Split → [Multiple Models] → Evaluation

**Use Case**: Compare different algorithms

```python
from backend.blocks import (
    DataSourceBlock, SplitBlock,
    CollaborativeFilteringBlock,
    MatrixFactorizationBlock,
    EvaluationBlock
)

# Shared data
data = DataSourceBlock('data')
data.configure(data_source='synthetic', n_interactions=5000)

split = SplitBlock('split')
split.configure(test_size=0.2)

data_out = data.execute({})
split_out = split.execute({'dataframe': data_out.data['dataframe']})

# Model 1: Collaborative Filtering
cf = CollaborativeFilteringBlock('cf')
cf.configure(method='user-based')
cf_out = cf.execute({'split-data': split_out.data['split-data']})

# Model 2: Matrix Factorization
mf = MatrixFactorizationBlock('mf')
mf.configure(method='svd', n_factors=50)
mf_out = mf.execute({'split-data': split_out.data['split-data']})

# Evaluate both
eval_block = EvaluationBlock('eval')
eval_block.configure(metrics=['rmse', 'mae', 'precision'])

cf_eval = eval_block.execute({'model': cf_out.data['model']})
mf_eval = eval_block.execute({'model': mf_out.data['model']})

print("Collaborative Filtering:", cf_eval.metrics)
print("Matrix Factorization:", mf_eval.metrics)
```

---

## Testing

### Run Frontend Tests

```bash
npm test              # Run tests in watch mode
npm test -- --run     # Run once
npm run test:ui       # Interactive UI
npm run test:coverage # With coverage report
```

### Run Backend Tests

```bash
cd backend
python tests/test_all_blocks.py
```

---

## Common Tasks

### Load Your Own Data

**CSV Format**:
```csv
user_id,item_id,rating,timestamp
1,101,5.0,1234567890
1,102,4.0,1234567891
2,101,3.0,1234567892
```

**Usage**:
```python
data = DataSourceBlock('data')
data.configure(
    data_source='csv',
    file_path='path/to/your/data.csv'
)
```

### Customize Components

Add new blocks by extending `BaseBlock`:

```python
from backend.blocks.base import BaseBlock, BlockOutput, BlockStatus

class CustomBlock(BaseBlock):
    def configure(self, **kwargs):
        self.config.update(kwargs)
        self.status = BlockStatus.CONFIGURED

    def validate_config(self):
        return []  # Return error messages

    def execute(self, inputs):
        # Your logic here
        return BlockOutput(
            block_id=self.block_id,
            status=BlockStatus.COMPLETED,
            data={'result': 'your_data'},
            metrics={'accuracy': 0.95}
        )

    def get_schema(self):
        return {
            'type': 'custom-block',
            'inputs': {'data': {'type': 'DataFrame'}},
            'outputs': {'result': {'type': 'Any'}},
            'config': {}
        }
```

### Export Workflows

Workflows are saved as JSON:

```json
{
  "components": [
    {
      "id": "component-1",
      "type": "data-source",
      "position": {"x": 100, "y": 100},
      "label": "Data Source",
      "config": {
        "dataSource": "synthetic",
        "n_users": 100
      }
    }
  ],
  "connections": [
    {
      "id": "component-1-component-2",
      "from": "component-1",
      "to": "component-2"
    }
  ]
}
```

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Delete` | Remove selected component |
| `Shift + Drag` | Pan canvas |
| `Mouse Wheel` | Zoom in/out |
| `Double Click` | Configure component |
| `Ctrl + S` | Save workflow |
| `Ctrl + Z` | Undo (planned) |

---

## Troubleshooting

### "Module not found" errors
```bash
npm install
cd backend && pip install -r requirements.txt
```

### Build fails
```bash
npm run lint  # Check for linting errors
npm test      # Run tests
```

### Tests fail
Make sure all dependencies are installed:
```bash
npm install --save-dev vitest @vitest/ui @testing-library/react
```

### Backend errors
Check Python version:
```bash
python --version  # Should be 3.11+
```

---

## Next Steps

- Read [FEATURES_AND_UPDATES.md](FEATURES_AND_UPDATES.md) for complete feature documentation
- Check [BLOCK_REVIEWS.md](BLOCK_REVIEWS.md) for block implementation details
- Explore example workflows in the frontend
- Join our community (coming soon)

---

## Resources

- **Documentation**: `/docs` folder
- **Examples**: See example workflows in this guide
- **Tests**: `src/**/*.test.ts` and `backend/tests/`
- **API Reference**: See block implementations in `backend/blocks/`

---

**Happy Recommending! 🎯**

For questions or issues, visit: https://github.com/JoeyManicotti/Mammoth/issues
