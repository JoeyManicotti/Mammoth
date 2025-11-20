"""Compare Random Forest vs XGBoost Performance"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from backend.blocks import DataSourceBlock, SplitBlock, RandomForestBlock, XGBoostBlock, EvaluationBlock

print("🔬 Model Comparison: Random Forest vs XGBoost\n")
print("=" * 60)

# Load data
print("\n📊 Loading test dataset...")
data_block = DataSourceBlock('data')
data_block.configure(data_source='synthetic', n_users=200, n_items=300, n_interactions=3000)
data_out = data_block.execute({})

if data_out.status.value != 'completed':
    print(f"✗ Data loading failed: {data_out.errors}")
    sys.exit(1)

print(f"✓ Data loaded: {data_out.metrics['n_rows']} interactions")

# Split data
split_block = SplitBlock('split')
split_block.configure(test_size=0.2, split_type='random')
split_out = split_block.execute({'dataframe': data_out.data['dataframe']})

if split_out.status.value != 'completed':
    print(f"✗ Split failed: {split_out.errors}")
    sys.exit(1)

print(f"✓ Split: {split_out.metrics['train_size']} train, {split_out.metrics['test_size']} test")

# Train Random Forest
print("\n" + "=" * 60)
print("🌲 Training Random Forest...")
print("=" * 60)
rf_block = RandomForestBlock('rf')
rf_block.configure(n_estimators=100, max_depth=10, min_samples_split=5)
rf_out = rf_block.execute({'split-data': split_out.data['split-data']})

if rf_out.status.value == 'completed':
    print(f"✓ Random Forest trained")
    print(f"  • Estimators: {rf_out.metrics['n_estimators']}")
    print(f"  • Features: {rf_out.metrics['n_features']} (includes std deviation)")
    print(f"  • Training samples: {rf_out.metrics['n_training_samples']}")

    # Evaluate
    eval_rf = EvaluationBlock('eval_rf')
    eval_rf.configure(metrics=['rmse', 'mae', 'precision', 'recall', 'ndcg'], k_values='5,10')
    eval_rf_out = eval_rf.execute({
        'model': rf_out.data['model'],
        'test_data': split_out.data['split-data']
    })

    if eval_rf_out.status.value == 'completed':
        rf_metrics = eval_rf_out.metrics
        print(f"\n  Random Forest Metrics:")
        print(f"    RMSE: {rf_metrics['rmse']:.4f}")
        print(f"    MAE: {rf_metrics['mae']:.4f}")
        print(f"    Precision@5: {rf_metrics['precision@5']:.4f}")
        print(f"    Recall@5: {rf_metrics['recall@5']:.4f}")
        print(f"    NDCG@5: {rf_metrics['ndcg@5']:.4f}")
else:
    print(f"✗ Random Forest failed: {rf_out.errors}")
    rf_metrics = None

# Train XGBoost
print("\n" + "=" * 60)
print("🚀 Training XGBoost...")
print("=" * 60)
xgb_block = XGBoostBlock('xgb')
xgb_block.configure(n_estimators=100, max_depth=6, learning_rate=0.1)
xgb_out = xgb_block.execute({'split-data': split_out.data['split-data']})

if xgb_out.status.value == 'completed':
    print(f"✓ XGBoost trained")
    print(f"  • Estimators: {xgb_out.metrics['n_estimators']}")
    print(f"  • Features: {xgb_out.metrics['n_features']}")
    print(f"  • Training samples: {xgb_out.metrics['n_training_samples']}")

    # Evaluate
    eval_xgb = EvaluationBlock('eval_xgb')
    eval_xgb.configure(metrics=['rmse', 'mae', 'precision', 'recall', 'ndcg'], k_values='5,10')
    eval_xgb_out = eval_xgb.execute({
        'model': xgb_out.data['model'],
        'test_data': split_out.data['split-data']
    })

    if eval_xgb_out.status.value == 'completed':
        xgb_metrics = eval_xgb_out.metrics
        print(f"\n  XGBoost Metrics:")
        print(f"    RMSE: {xgb_metrics['rmse']:.4f}")
        print(f"    MAE: {xgb_metrics['mae']:.4f}")
        print(f"    Precision@5: {xgb_metrics['precision@5']:.4f}")
        print(f"    Recall@5: {xgb_metrics['recall@5']:.4f}")
        print(f"    NDCG@5: {xgb_metrics['ndcg@5']:.4f}")
else:
    print(f"✗ XGBoost failed: {xgb_out.errors}")
    xgb_metrics = None

# Comparison
if rf_metrics and xgb_metrics:
    print("\n" + "=" * 60)
    print("📊 Model Comparison Summary")
    print("=" * 60)

    print(f"\n{'Metric':<20} {'Random Forest':<15} {'XGBoost':<15} {'Winner':<10}")
    print("-" * 60)

    metrics_to_compare = [
        ('RMSE (lower)', 'rmse', 'lower'),
        ('MAE (lower)', 'mae', 'lower'),
        ('Precision@5', 'precision@5', 'higher'),
        ('Recall@5', 'recall@5', 'higher'),
        ('NDCG@5', 'ndcg@5', 'higher'),
    ]

    rf_wins = 0
    xgb_wins = 0

    for metric_name, metric_key, direction in metrics_to_compare:
        rf_val = rf_metrics[metric_key]
        xgb_val = xgb_metrics[metric_key]

        if direction == 'lower':
            winner = 'RF' if rf_val < xgb_val else 'XGB'
            if rf_val < xgb_val:
                rf_wins += 1
            else:
                xgb_wins += 1
        else:
            winner = 'RF' if rf_val > xgb_val else 'XGB'
            if rf_val > xgb_val:
                rf_wins += 1
            else:
                xgb_wins += 1

        print(f"{metric_name:<20} {rf_val:<15.4f} {xgb_val:<15.4f} {winner:<10}")

    print("-" * 60)
    print(f"\n🏆 Overall: Random Forest: {rf_wins} wins, XGBoost: {xgb_wins} wins")

    print("\n📝 Key Differences:")
    print("  • Random Forest: 9 features (includes std deviation)")
    print("  • XGBoost: 7 features (faster, gradient boosting)")
    print("  • Random Forest: Better for noisy data")
    print("  • XGBoost: Better for structured patterns")

print("\n✨ Comparison test completed!")
