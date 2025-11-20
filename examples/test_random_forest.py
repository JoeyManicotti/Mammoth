"""Test Random Forest Block Implementation"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from backend.blocks import DataSourceBlock, SplitBlock, RandomForestBlock, EvaluationBlock

print("🧪 Testing Random Forest Implementation\n")

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

# 3. Train Random Forest
print("\n3️⃣  Training Random Forest model...")
rf_block = RandomForestBlock('rf')
rf_block.configure(n_estimators=50, max_depth=8, min_samples_split=5)
rf_out = rf_block.execute({'split-data': split_out.data['split-data']})

if rf_out.status.value == 'completed':
    print(f"   ✓ Model trained successfully")
    print(f"     n_estimators: {rf_out.metrics['n_estimators']}")
    print(f"     n_features: {rf_out.metrics['n_features']}")
    print(f"     n_training_samples: {rf_out.metrics['n_training_samples']}")
    print(f"     predictions_shape: {rf_out.metrics['predictions_shape']}")
    if 'feature_importance_top5' in rf_out.metrics:
        print(f"     top_features: {rf_out.metrics['feature_importance_top5']}")
else:
    print(f"   ✗ Failed: {rf_out.errors}")
    sys.exit(1)

# 4. Evaluate
print("\n4️⃣  Evaluating model...")
eval_block = EvaluationBlock('eval')
eval_block.configure(metrics=['rmse', 'mae', 'precision', 'recall', 'ndcg'], k_values='5,10')
eval_out = eval_block.execute({
    'model': rf_out.data['model'],
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

print("\n✨ Random Forest test completed successfully!")

# 5. Test with Kaggle data
print("\n\n🧪 Testing with Kaggle Dataset (MovieLens)...\n")

data_block2 = DataSourceBlock('data2')
data_block2.configure(data_source='kaggle', kaggle_dataset='movielens-100k')
data_out2 = data_block2.execute({})

if data_out2.status.value == 'completed':
    print(f"   ✓ MovieLens data loaded: {data_out2.metrics['n_rows']} interactions")

    # Split
    split_block2 = SplitBlock('split2')
    split_block2.configure(test_size=0.2, split_type='random')
    split_out2 = split_block2.execute({'dataframe': data_out2.data['dataframe']})

    if split_out2.status.value == 'completed':
        print(f"   ✓ Split complete: {split_out2.metrics['train_size']} train, {split_out2.metrics['test_size']} test")

        # Train smaller model for larger dataset
        rf_block2 = RandomForestBlock('rf2')
        rf_block2.configure(n_estimators=30, max_depth=6)
        rf_out2 = rf_block2.execute({'split-data': split_out2.data['split-data']})

        if rf_out2.status.value == 'completed':
            print(f"   ✓ Model trained on MovieLens")
            print(f"     n_training_samples: {rf_out2.metrics['n_training_samples']}")

            # Evaluate
            eval_block2 = EvaluationBlock('eval2')
            eval_block2.configure(metrics=['rmse', 'mae', 'precision'], k_values='10')
            eval_out2 = eval_block2.execute({
                'model': rf_out2.data['model'],
                'test_data': split_out2.data['split-data']
            })

            if eval_out2.status.value == 'completed':
                print(f"   ✓ Evaluation complete on real data\n")
                print("     Metrics:")
                for metric, value in eval_out2.metrics.items():
                    print(f"       {metric}: {value:.4f}")
            else:
                print(f"   ⚠ Evaluation failed: {eval_out2.errors}")
        else:
            print(f"   ⚠ Training failed: {rf_out2.errors}")
    else:
        print(f"   ⚠ Split failed: {split_out2.errors}")
else:
    print(f"   ⚠ Data loading failed (may need download): {data_out2.errors}")

print("\n✨ All Random Forest tests completed!")
