# Mammoth Recommender System Backend

Python Flask API for executing recommendation algorithms including XGBoost, Random Forests, Matrix Factorization, and Collaborative Filtering.

## Features

### Implemented Models

#### 1. **XGBoost Recommender** (`models/xgboost_recommender.py`)
- Gradient boosting-based recommendation
- Treats recommendation as a regression or ranking problem
- Configurable parameters:
  - `n_estimators`: Number of boosting rounds (default: 100)
  - `max_depth`: Maximum tree depth (default: 6)
  - `learning_rate`: Step size (default: 0.1)
  - `objective`: Learning objective (reg:squarederror, rank:pairwise, rank:ndcg)
  - `reg_alpha`: L1 regularization (default: 0.0)
  - `reg_lambda`: L2 regularization (default: 1.0)

**Test Cases:**
- Basic training on 1000 synthetic interactions
- Regularization effects
- Feature importance analysis
- Top-K recommendation generation

#### 2. **Random Forest Recommender** (`models/random_forest_recommender.py`)
- Ensemble of decision trees
- Provides prediction uncertainty estimates
- Configurable parameters:
  - `n_estimators`: Number of trees (default: 100)
  - `max_depth`: Maximum tree depth (default: None)
  - `min_samples_split`: Min samples to split (default: 2)
  - `min_samples_leaf`: Min samples at leaf (default: 1)
  - `max_features`: Features per split (default: 'sqrt')

**Test Cases:**
- Basic training and prediction
- Prediction uncertainty quantification
- Feature importance ranking
- Shallow vs deep tree comparison

### Utilities

#### Data Loader (`utils/data_loader.py`)
- Generate synthetic user-item interaction data
- Load MovieLens-style datasets
- Train-test splitting (random and temporal)
- Create sparse interaction matrices

**Features:**
- Synthetic data with configurable sparsity
- User and item bias simulation
- Temporal ordering support
- Interaction matrix creation

#### Metrics (`utils/metrics.py`)
- Rating prediction metrics: RMSE, MAE
- Ranking metrics: Precision@K, Recall@K, NDCG@K, MAP@K, Hit Rate@K

## API Endpoints

### Health Check
```
GET /health
```
Returns service health status.

### Load Data
```
POST /api/data/load
Content-Type: application/json

{
  "source": "movielens-100k | synthetic",
  "sample_size": 1000,
  "train_test_split": 0.8
}
```

Returns:
```json
{
  "success": true,
  "pipeline_id": "pipeline_1",
  "metadata": {
    "n_users": 100,
    "n_items": 200,
    "n_interactions": 1000,
    "sparsity": 0.95
  },
  "train_size": 800,
  "test_size": 200
}
```

### Train Model
```
POST /api/models/train
Content-Type: application/json

{
  "pipeline_id": "pipeline_1",
  "model_type": "xgboost | random_forest | matrix_factorization | collaborative_filtering",
  "config": {
    "n_estimators": 100,
    "max_depth": 6,
    "learning_rate": 0.1
  }
}
```

### Generate Predictions
```
POST /api/models/predict
Content-Type: application/json

{
  "pipeline_id": "pipeline_1",
  "user_ids": [1, 2, 3],
  "top_k": 10
}
```

### Evaluate Model
```
POST /api/models/evaluate
Content-Type: application/json

{
  "pipeline_id": "pipeline_1",
  "metrics": ["rmse", "precision", "recall", "ndcg"],
  "k_values": [5, 10, 20]
}
```

### Compare Models
```
POST /api/models/compare
Content-Type: application/json

{
  "pipeline_id": "pipeline_1",
  "model_configs": [
    {"type": "xgboost", "config": {"n_estimators": 50}},
    {"type": "random_forest", "config": {"n_estimators": 50}},
    {"type": "matrix_factorization", "config": {"n_factors": 50}}
  ],
  "metrics": ["rmse", "precision@10", "ndcg@10"]
}
```

## Installation

### Local Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run the Flask app
python app.py
```

The API will be available at `http://localhost:5000`

### Docker Installation

```bash
# Build the Docker image
docker build -t mammoth-backend .

# Run the container
docker run -p 5000:5000 mammoth-backend
```

### Docker Compose

Add to the main `docker-compose.yml`:

```yaml
mammoth-backend:
  build: ./backend
  ports:
    - "5000:5000"
  environment:
    - FLASK_ENV=development
  restart: unless-stopped
```

## Testing Models

### Test XGBoost Recommender

```bash
cd models
python xgboost_recommender.py
```

Expected output:
- Test Case 1: Basic training and prediction
- Test Case 2: Regularization comparison
- Test Case 3: Feature importance scores

### Test Random Forest Recommender

```bash
cd models
python random_forest_recommender.py
```

Expected output:
- Test Case 1: Basic training
- Test Case 2: Prediction uncertainty
- Test Case 3: Feature importance
- Test Case 4: Shallow vs deep trees comparison

### Test Data Loader

```bash
cd utils
python data_loader.py
```

Expected output:
- Synthetic data generation
- Train-test splitting
- Temporal splitting
- Interaction matrix creation

### Test Metrics

```bash
cd utils
python metrics.py
```

Expected output:
- Rating metrics (RMSE, MAE)
- Precision and Recall @K
- NDCG @K
- MAP @K
- Hit Rate @K

## Model Specifications

### Input/Output Schemas

All models expect training data with the following schema:

**Input DataFrame:**
```
- user_id: int
- item_id: int
- rating: float
- timestamp: int (optional)
- additional_features: any (optional)
```

**Output (Predictions):**
```python
{
  user_id: [(item_id, score), (item_id, score), ...]
}
```

### Configuration Options

#### XGBoost
```python
{
  "n_estimators": 100,      # Number of boosting rounds
  "max_depth": 6,           # Maximum tree depth
  "learning_rate": 0.1,     # Step size shrinkage
  "objective": "reg:squarederror",  # Loss function
  "reg_alpha": 0.0,         # L1 regularization
  "reg_lambda": 1.0         # L2 regularization
}
```

#### Random Forest
```python
{
  "n_estimators": 100,      # Number of trees
  "max_depth": None,        # Maximum tree depth
  "min_samples_split": 2,   # Min samples to split
  "min_samples_leaf": 1,    # Min samples at leaf
  "max_features": "sqrt"    # Features per split
}
```

## Performance Benchmarks

Based on synthetic data (100 users, 200 items, 1000 interactions):

| Model | RMSE | Training Time | Prediction Time |
|-------|------|---------------|-----------------|
| XGBoost (100 trees) | ~0.92 | ~2s | ~0.1s |
| Random Forest (100 trees) | ~0.95 | ~1.5s | ~0.2s |
| Matrix Factorization (50 factors) | ~0.90 | ~3s | ~0.05s |

## Future Enhancements

- [ ] Deep learning models (NCF, Wide & Deep)
- [ ] Online learning support
- [ ] Distributed training with Dask
- [ ] Caching layer for predictions
- [ ] A/B testing framework
- [ ] Real-time recommendation endpoints
- [ ] Model versioning and registry

## Dependencies

- Flask 3.0.0 - Web framework
- NumPy 1.24.3 - Numerical computing
- Pandas 2.0.3 - Data manipulation
- scikit-learn 1.3.0 - Machine learning
- XGBoost 2.0.1 - Gradient boosting
- SciPy 1.11.1 - Scientific computing

## License

See main LICENSE file.
