"""Comprehensive CV Pipeline Comparison"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from backend.cv_blocks import (
    CVDataSourceBlock,
    TemplateMatcherBlock,
    FeatureMatcherBlock,
    TrackerBlock,
    CVEvaluationBlock
)

print("🔬 Comprehensive CV Pipeline Comparison\n")
print("=" * 70)

# 1. Load synthetic tracking data
print("\n📊 Loading test dataset...")
data_block = CVDataSourceBlock('data')
data_block.configure(source='synthetic', n_frames=100, width=800, height=600, object_size=80)
data_out = data_block.execute({})

if data_out.status.value != 'completed':
    print(f"✗ Data loading failed: {data_out.errors}")
    sys.exit(1)

print(f"✓ Data loaded: {data_out.metrics['n_frames']} frames")
print(f"  Resolution: {data_out.metrics['width']}x{data_out.metrics['height']}")

# Define methods to test
methods = [
    ('Template: CCOEFF', 'template', {'method': 'ccoeff_normed'}),
    ('Template: CCORR', 'template', {'method': 'ccorr_normed'}),
    ('Feature: ORB', 'feature', {'method': 'orb'}),
    ('Feature: AKAZE', 'feature', {'method': 'akaze'}),
    ('Tracker: KCF', 'tracker', {'tracker_type': 'kcf'}),
    ('Tracker: CSRT', 'tracker', {'tracker_type': 'csrt'}),
    ('Tracker: MOSSE', 'tracker', {'tracker_type': 'mosse'}),
]

results = []

# Test each method
for method_name, method_type, config in methods:
    print(f"\n{'='*70}")
    print(f"Testing: {method_name}")
    print(f"{'='*70}")

    try:
        # Create appropriate block
        if method_type == 'template':
            block = TemplateMatcherBlock(f'block_{len(results)}')
        elif method_type == 'feature':
            block = FeatureMatcherBlock(f'block_{len(results)}')
        elif method_type == 'tracker':
            block = TrackerBlock(f'block_{len(results)}')

        block.configure(**config)

        # Execute
        block_out = block.execute({
            'frames': data_out.data['frames'],
            'init_bbox': data_out.data['init_bbox']
        })

        if block_out.status.value == 'completed':
            print(f"✓ {method_name} complete")

            # Evaluate
            eval_block = CVEvaluationBlock(f'eval_{len(results)}')
            eval_block.configure(
                metrics=['iou', 'center_error', 'precision', 'success_plot'],
                iou_thresholds=[0.3, 0.5, 0.7]
            )
            eval_out = eval_block.execute({
                'tracked_boxes': block_out.data['tracked_boxes'],
                'ground_truth': data_out.data['ground_truth']
            })

            if eval_out.status.value == 'completed':
                metrics = eval_out.metrics
                print(f"  Avg IoU: {metrics['avg_iou']:.4f}")
                print(f"  Avg Center Error: {metrics['avg_center_error']:.2f} px")
                print(f"  Precision@0.5: {metrics['precision@0.5']:.4f}")
                print(f"  AUC: {metrics['auc']:.4f}")

                results.append({
                    'name': method_name,
                    'type': method_type,
                    'metrics': metrics
                })
            else:
                print(f"⚠ Evaluation failed: {eval_out.errors}")
        else:
            print(f"✗ Failed: {block_out.errors}")

    except Exception as e:
        print(f"✗ Error: {e}")

# Generate comparison report
print(f"\n{'='*70}")
print("📊 FINAL COMPARISON")
print(f"{'='*70}")

if results:
    # Sort by average IoU
    results_sorted = sorted(results, key=lambda x: x['metrics']['avg_iou'], reverse=True)

    print(f"\n{'Method':<25} {'Avg IoU':<12} {'Prec@0.5':<12} {'Center Err':<12} {'AUC':<10}")
    print("-" * 70)

    for result in results_sorted:
        name = result['name']
        m = result['metrics']
        print(f"{name:<25} {m['avg_iou']:<12.4f} {m['precision@0.5']:<12.4f} "
              f"{m['avg_center_error']:<12.2f} {m['auc']:<10.4f}")

    # Category winners
    print(f"\n{'='*70}")
    print("🏆 Category Winners")
    print(f"{'='*70}")

    categories = {
        'template': 'Template Matching',
        'feature': 'Feature Matching',
        'tracker': 'Object Tracking'
    }

    for cat_key, cat_name in categories.items():
        cat_results = [r for r in results_sorted if r['type'] == cat_key]
        if cat_results:
            best = cat_results[0]
            print(f"\n{cat_name}:")
            print(f"  Winner: {best['name']}")
            print(f"  IoU: {best['metrics']['avg_iou']:.4f}")
            print(f"  Precision@0.5: {best['metrics']['precision@0.5']:.4f}")

    # Overall winner
    print(f"\n{'='*70}")
    best_overall = results_sorted[0]
    print(f"🥇 Overall Best Method: {best_overall['name']}")
    print(f"   Avg IoU: {best_overall['metrics']['avg_iou']:.4f}")
    print(f"   Avg Center Error: {best_overall['metrics']['avg_center_error']:.2f} px")
    print(f"   AUC: {best_overall['metrics']['auc']:.4f}")

    # Method recommendations
    print(f"\n{'='*70}")
    print("💡 Method Recommendations")
    print(f"{'='*70}")

    print("\nTemplate Matching:")
    print("  • Fast and simple")
    print("  • Best for rigid objects with consistent appearance")
    print("  • Struggles with rotation and scale changes")

    print("\nFeature Matching:")
    print("  • Robust to rotation and scale")
    print("  • Best for textured objects")
    print("  • Slower than template matching")

    print("\nObject Tracking:")
    print("  • Adaptive to appearance changes")
    print("  • Best for long-term tracking")
    print("  • Can fail and lose target")
    print("  • CSRT: Most accurate, slower")
    print("  • KCF: Good balance of speed and accuracy")
    print("  • MOSSE: Fastest, lower accuracy")

print("\n✨ Comprehensive CV tests completed!")
