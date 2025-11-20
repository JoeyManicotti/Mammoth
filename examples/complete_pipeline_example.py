"""
Complete Pipeline Example

Demonstrates how to build and execute a full recommendation pipeline
from data loading to evaluation.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / 'backend'))

from blocks import (
    DataSourceBlock,
    SplitBlock,
    CollaborativeFilteringBlock,
    MatrixFactorizationBlock,
    PredictionsBlock,
    EvaluationBlock
)
import time


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_metrics(metrics: dict, indent: int = 2):
    """Pretty print metrics"""
    spaces = " " * indent
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"{spaces}{key}: {value:.4f}")
        else:
            print(f"{spaces}{key}: {value}")


def run_collaborative_filtering_pipeline():
    """
    Example 1: Collaborative Filtering Pipeline

    Data Source → Split → Collaborative Filter → Predictions & Evaluation
    """
    print_section("Example 1: Collaborative Filtering Pipeline")

    start_time = time.time()

    # Step 1: Load Data
    print("\n1️⃣  Loading synthetic data...")
    data_block = DataSourceBlock('data-source')
    data_block.configure(
        data_source='synthetic',
        n_users=200,
        n_items=300,
        n_interactions=3000
    )
    data_output = data_block.execute({})

    if data_output.status.value == 'completed':
        print("   ✓ Data loaded successfully")
        print_metrics(data_output.metrics, indent=5)
    else:
        print(f"   ✗ Error: {data_output.errors}")
        return

    # Step 2: Split Data
    print("\n2️⃣  Splitting into train/test sets...")
    split_block = SplitBlock('split')
    split_block.configure(
        test_size=0.2,
        method='random'
    )
    split_output = split_block.execute({
        'dataframe': data_output.data['dataframe']
    })

    if split_output.status.value == 'completed':
        print("   ✓ Data split successfully")
        print_metrics(split_output.metrics, indent=5)
    else:
        print(f"   ✗ Error: {split_output.errors}")
        return

    # Step 3: Train Collaborative Filter
    print("\n3️⃣  Training collaborative filtering model...")
    cf_block = CollaborativeFilteringBlock('cf-model')
    cf_block.configure(
        method='user-based',
        k_neighbors=50
    )
    cf_output = cf_block.execute({
        'split-data': split_output.data['split-data']
    })

    if cf_output.status.value == 'completed':
        print("   ✓ Model trained successfully")
        print_metrics(cf_output.metrics, indent=5)
    else:
        print(f"   ✗ Error: {cf_output.errors}")
        return

    # Step 4: Generate Predictions
    print("\n4️⃣  Generating top-10 recommendations...")
    pred_block = PredictionsBlock('predictions')
    pred_block.configure(top_k=10)
    pred_output = pred_block.execute({
        'model': cf_output.data['model']
    })

    if pred_output.status.value == 'completed':
        print("   ✓ Predictions generated")
        print_metrics(pred_output.metrics, indent=5)

        # Show sample recommendations
        recommendations = pred_output.data['recommendations']
        sample_user = list(recommendations.keys())[0]
        print(f"\n     Sample recommendations for user {sample_user}:")
        for item_id, score in recommendations[sample_user][:5]:
            print(f"       - Item {item_id}: {score:.2f}")
    else:
        print(f"   ✗ Error: {pred_output.errors}")
        return

    # Step 5: Evaluate
    print("\n5️⃣  Evaluating model performance...")
    eval_block = EvaluationBlock('evaluation')
    eval_block.configure(
        metrics=['rmse', 'mae', 'precision', 'recall', 'ndcg']
    )
    eval_output = eval_block.execute({
        'model': cf_output.data['model']
    })

    if eval_output.status.value == 'completed':
        print("   ✓ Evaluation complete")
        print("\n     Metrics:")
        print_metrics(eval_output.metrics, indent=7)
    else:
        print(f"   ✗ Error: {eval_output.errors}")
        return

    elapsed = time.time() - start_time
    print(f"\n✨ Pipeline completed in {elapsed:.2f} seconds")


def run_matrix_factorization_pipeline():
    """
    Example 2: Matrix Factorization Pipeline

    Data Source → Split → Matrix Factorization → Evaluation
    """
    print_section("Example 2: Matrix Factorization Pipeline")

    start_time = time.time()

    # Load and split data
    print("\n📊 Preparing data...")
    data_block = DataSourceBlock('data')
    data_block.configure(
        data_source='synthetic',
        n_users=150,
        n_items=200,
        n_interactions=2000
    )
    data_output = data_block.execute({})

    split_block = SplitBlock('split')
    split_block.configure(test_size=0.2, method='temporal')
    split_output = split_block.execute({
        'dataframe': data_output.data['dataframe']
    })

    print("   ✓ Data prepared")

    # Train Matrix Factorization
    print("\n🔢 Training SVD model...")
    mf_block = MatrixFactorizationBlock('mf-model')
    mf_block.configure(
        method='svd',
        n_factors=50,
        n_epochs=20
    )
    mf_output = mf_block.execute({
        'split-data': split_output.data['split-data']
    })

    if mf_output.status.value == 'completed':
        print("   ✓ SVD model trained")
        print_metrics(mf_output.metrics, indent=5)
    else:
        print(f"   ✗ Error: {mf_output.errors}")
        return

    # Evaluate
    print("\n📈 Evaluating...")
    eval_block = EvaluationBlock('eval')
    eval_block.configure(metrics=['rmse', 'mae'])
    eval_output = eval_block.execute({
        'model': mf_output.data['model']
    })

    print("   ✓ Results:")
    print_metrics(eval_output.metrics, indent=5)

    elapsed = time.time() - start_time
    print(f"\n✨ Pipeline completed in {elapsed:.2f} seconds")


def run_model_comparison():
    """
    Example 3: Compare Multiple Models

    Data Source → Split → [CF, MF] → Evaluation
    """
    print_section("Example 3: Model Comparison")

    # Prepare shared data
    print("\n📊 Preparing shared dataset...")
    data_block = DataSourceBlock('data')
    data_block.configure(
        data_source='synthetic',
        n_users=100,
        n_items=150,
        n_interactions=1500
    )
    data_output = data_block.execute({})

    split_block = SplitBlock('split')
    split_block.configure(test_size=0.2)
    split_output = split_block.execute({
        'dataframe': data_output.data['dataframe']
    })

    print("   ✓ Data ready for training")

    results = {}

    # Model 1: Collaborative Filtering
    print("\n🤝 Training Collaborative Filtering...")
    cf_block = CollaborativeFilteringBlock('cf')
    cf_block.configure(method='user-based')
    cf_output = cf_block.execute({
        'split-data': split_output.data['split-data']
    })

    eval_block = EvaluationBlock('eval-cf')
    eval_block.configure(metrics=['rmse', 'mae', 'precision'])
    cf_eval = eval_block.execute({'model': cf_output.data['model']})
    results['Collaborative Filtering'] = cf_eval.metrics
    print("   ✓ CF trained and evaluated")

    # Model 2: Matrix Factorization
    print("\n🔢 Training Matrix Factorization...")
    mf_block = MatrixFactorizationBlock('mf')
    mf_block.configure(method='svd', n_factors=30)
    mf_output = mf_block.execute({
        'split-data': split_output.data['split-data']
    })

    eval_block = EvaluationBlock('eval-mf')
    eval_block.configure(metrics=['rmse', 'mae', 'precision'])
    mf_eval = eval_block.execute({'model': mf_output.data['model']})
    results['Matrix Factorization'] = mf_eval.metrics
    print("   ✓ MF trained and evaluated")

    # Compare results
    print("\n📊 Comparison Results:")
    print()
    print("     Model                      RMSE     MAE      Precision")
    print("     " + "-" * 60)
    for model_name, metrics in results.items():
        rmse = metrics.get('rmse', 0)
        mae = metrics.get('mae', 0)
        prec = metrics.get('precision@10', 0)
        print(f"     {model_name:25} {rmse:.4f}   {mae:.4f}   {prec:.4f}")

    print()
    # Determine winner
    best_model = min(results.items(), key=lambda x: x[1].get('rmse', float('inf')))
    print(f"     🏆 Best Model (by RMSE): {best_model[0]}")


def main():
    """Run all examples"""
    print("\n" + "🎯" * 35)
    print("         MAMMOTH COMPLETE PIPELINE EXAMPLES")
    print("🎯" * 35)

    try:
        # Example 1: Full CF Pipeline
        run_collaborative_filtering_pipeline()

        # Example 2: Matrix Factorization
        run_matrix_factorization_pipeline()

        # Example 3: Model Comparison
        run_model_comparison()

        print("\n" + "=" * 70)
        print("  All examples completed successfully! ✨")
        print("=" * 70)
        print()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
