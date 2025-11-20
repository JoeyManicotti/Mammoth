"""Test Template Matching Implementation"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from backend.cv_blocks import CVDataSourceBlock, TemplateMatcherBlock, CVEvaluationBlock

print("🎯 Testing Template Matching\n")
print("=" * 60)

# 1. Load synthetic tracking data
print("\n1️⃣  Loading synthetic tracking data...")
data_block = CVDataSourceBlock('data')
data_block.configure(source='synthetic', n_frames=50, width=640, height=480, object_size=50)
data_out = data_block.execute({})

if data_out.status.value == 'completed':
    print(f"   ✓ Data loaded: {data_out.metrics['n_frames']} frames")
    print(f"     Resolution: {data_out.metrics['width']}x{data_out.metrics['height']}")
else:
    print(f"   ✗ Failed: {data_out.errors}")
    sys.exit(1)

# Test different template matching methods
methods = ['ccoeff_normed', 'ccorr_normed', 'sqdiff_normed']

results = {}

for method in methods:
    print(f"\n{'='*60}")
    print(f"2️⃣  Testing {method.upper()} method...")
    print(f"{'='*60}")

    # Template matching
    tm_block = TemplateMatcherBlock(f'tm_{method}')
    tm_block.configure(method=method, update_template=False)
    tm_out = tm_block.execute({
        'frames': data_out.data['frames'],
        'init_bbox': data_out.data['init_bbox']
    })

    if tm_out.status.value == 'completed':
        print(f"   ✓ Template matching complete")
        print(f"     Method: {tm_out.metrics['method']}")
        print(f"     Avg match score: {tm_out.metrics['avg_match_score']:.4f}")
        print(f"     Min/Max score: {tm_out.metrics['min_match_score']:.4f} / {tm_out.metrics['max_match_score']:.4f}")

        # Evaluate
        eval_block = CVEvaluationBlock(f'eval_{method}')
        eval_block.configure(
            metrics=['iou', 'center_error', 'precision'],
            iou_thresholds=[0.3, 0.5, 0.7]
        )
        eval_out = eval_block.execute({
            'tracked_boxes': tm_out.data['tracked_boxes'],
            'ground_truth': data_out.data['ground_truth']
        })

        if eval_out.status.value == 'completed':
            print(f"\n   📊 Evaluation Metrics:")
            print(f"     Avg IoU: {eval_out.metrics['avg_iou']:.4f}")
            print(f"     Avg Center Error: {eval_out.metrics['avg_center_error']:.2f} pixels")
            print(f"     Precision@0.5: {eval_out.metrics['precision@0.5']:.4f}")
            print(f"     Precision@0.7: {eval_out.metrics['precision@0.7']:.4f}")

            results[method] = eval_out.metrics
        else:
            print(f"   ⚠ Evaluation failed: {eval_out.errors}")
    else:
        print(f"   ✗ Template matching failed: {tm_out.errors}")

# Test with template updating
print(f"\n{'='*60}")
print(f"3️⃣  Testing with template updating...")
print(f"{'='*60}")

tm_update_block = TemplateMatcherBlock('tm_update')
tm_update_block.configure(method='ccoeff_normed', update_template=True, update_frequency=10)
tm_update_out = tm_update_block.execute({
    'frames': data_out.data['frames'],
    'init_bbox': data_out.data['init_bbox']
})

if tm_update_out.status.value == 'completed':
    print(f"   ✓ Template matching with updates complete")
    print(f"     Avg match score: {tm_update_out.metrics['avg_match_score']:.4f}")

    eval_update = CVEvaluationBlock('eval_update')
    eval_update.configure(metrics=['iou', 'center_error'])
    eval_update_out = eval_update.execute({
        'tracked_boxes': tm_update_out.data['tracked_boxes'],
        'ground_truth': data_out.data['ground_truth']
    })

    if eval_update_out.status.value == 'completed':
        print(f"\n   📊 With Template Updating:")
        print(f"     Avg IoU: {eval_update_out.metrics['avg_iou']:.4f}")
        print(f"     Avg Center Error: {eval_update_out.metrics['avg_center_error']:.2f} pixels")

        # Compare with static template
        static_iou = results['ccoeff_normed']['avg_iou']
        update_iou = eval_update_out.metrics['avg_iou']
        improvement = ((update_iou - static_iou) / static_iou * 100) if static_iou > 0 else 0

        print(f"\n   📈 Comparison:")
        print(f"     Static template IoU: {static_iou:.4f}")
        print(f"     Updated template IoU: {update_iou:.4f}")
        print(f"     Improvement: {improvement:+.2f}%")

# Summary
print(f"\n{'='*60}")
print("📊 Template Matching Summary")
print(f"{'='*60}")

print(f"\n{'Method':<20} {'Avg IoU':<12} {'Precision@0.5':<15}")
print("-" * 60)

for method, metrics in results.items():
    iou = metrics['avg_iou']
    prec = metrics['precision@0.5']
    print(f"{method:<20} {iou:<12.4f} {prec:<15.4f}")

print("\n✨ Template matching tests completed!")
