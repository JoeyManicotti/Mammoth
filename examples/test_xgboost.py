"""Test XGBoost Block Implementation"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from backend.blocks import DataSourceBlock, SplitBlock, XGBoostBlock, EvaluationBlock

print("🧪 Testing XGBoost Implementation\n")

# 1. Load data
print("1️⃣  Loading data...")
data_block = DataSourceBlock('data')
data_block.configure(data_source='synthetic', n_users=100, n_items=150, n_interactions=1500)
data_out = data_block.execute({})

if data_out.status.value == 'completed':
    print(f"   ✓ Data loaded: {data_out.metrics['n_rows']} interactions")
else:
    print(f"   ✗ Failed: {data_out.errors}")
    sys.exit(1)

# 2. Split data
print("\n2️⃣  Splitting data...")
split_block = SplitBlock('split')
split_block.configure(test_size=0.2, split_type='random')
split_out = split_block.execute({'dataframe': data_out.data['dataframe']})

if split_out.status.value == 'completed':
    print(f"   ✓ Split complete: {split_out.metrics['train_size']} train, {split_out.metrics['test_size']} test")
else:
    print(f"   ✗ Failed: {split_out.errors}")
    sys.exit(1)

# 3. Train XGBoost
print("\n3️⃣  Training XGBoost model...")
xgb_block = XGBoostBlock('xgb')
xgb_block.configure(n_estimators=50, max_depth=4, learning_rate=0.1)
xgb_out = xgb_block.execute({'split-data': split_out.data['split-data']})

if xgb_out.status.value == 'completed':
    print(f"   ✓ Model trained successfully")
    print(f"     n_estimators: {xgb_out.metrics['n_estimators']}")
    print(f"     n_features: {xgb_out.metrics['n_features']}")
    print(f"     n_training_samples: {xgb_out.metrics['n_training_samples']}")
    print(f"     predictions_shape: {xgb_out.metrics['predictions_shape']}")
else:
    print(f"   ✗ Failed: {xgb_out.errors}")
    sys.exit(1)

# 4. Evaluate
print("\n4️⃣  Evaluating model...")
eval_block = EvaluationBlock('eval')
eval_block.configure(metrics=['rmse', 'mae', 'precision', 'recall', 'ndcg'], k_values='5,10')
eval_out = eval_block.execute({
    'model': xgb_out.data['model'],
    'test_data': split_out.data['split-data']
})

if eval_out.status.value == 'completed':
    print(f"   ✓ Evaluation complete\n")
    print("     Metrics:")
    for metric, value in eval_out.metrics.items():
        print(f"       {metric}: {value:.4f}")
else:
    print(f"   ✗ Failed: {eval_out.errors}")
    sys.exit(1)

print("\n✨ XGBoost test completed successfully!")
