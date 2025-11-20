"""Test Object Tracking Algorithms"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from backend.cv_blocks import CVDataSourceBlock, TrackerBlock, CVEvaluationBlock

print("🎯 Testing Object Tracking Algorithms\n")
print("=" * 60)

# 1. Load synthetic tracking data
print("\n1️⃣  Loading synthetic tracking data...")
data_block = CVDataSourceBlock('data')
data_block.configure(source='synthetic', n_frames=80, width=640, height=480, object_size=60)
data_out = data_block.execute({})

if data_out.status.value == 'completed':
    print(f"   ✓ Data loaded: {data_out.metrics['n_frames']} frames")
    print(f"     Resolution: {data_out.metrics['width']}x{data_out.metrics['height']}")
else:
    print(f"   ✗ Failed: {data_out.errors}")
    sys.exit(1)

# Test different tracking algorithms
trackers = ['kcf', 'csrt', 'mosse', 'mil']

results = {}

for tracker_type in trackers:
    print(f"\n{'='*60}")
    print(f"2️⃣  Testing {tracker_type.upper()} tracker...")
    print(f"{'='*60}")

    # Track object
    tracker_block = TrackerBlock(f'tracker_{tracker_type}')
    tracker_block.configure(tracker_type=tracker_type, reinit_on_fail=False)
    tracker_out = tracker_block.execute({
        'frames': data_out.data['frames'],
        'init_bbox': data_out.data['init_bbox']
    })

    if tracker_out.status.value == 'completed':
        print(f"   ✓ Tracking complete")
        print(f"     Tracker: {tracker_out.metrics['tracker_type']}")
        print(f"     Success rate: {tracker_out.metrics['success_rate']:.2%}")
        print(f"     Failures: {tracker_out.metrics['n_failures']}")
        print(f"     Avg confidence: {tracker_out.metrics['avg_confidence']:.4f}")

        # Evaluate
        eval_block = CVEvaluationBlock(f'eval_{tracker_type}')
        eval_block.configure(
            metrics=['iou', 'center_error', 'precision', 'success_plot'],
            iou_thresholds=[0.3, 0.5, 0.7]
        )
        eval_out = eval_block.execute({
            'tracked_boxes': tracker_out.data['tracked_boxes'],
            'ground_truth': data_out.data['ground_truth']
        })

        if eval_out.status.value == 'completed':
            print(f"\n   📊 Evaluation Metrics:")
            print(f"     Avg IoU: {eval_out.metrics['avg_iou']:.4f}")
            print(f"     Avg Center Error: {eval_out.metrics['avg_center_error']:.2f} pixels")
            print(f"     Max Center Error: {eval_out.metrics['max_center_error']:.2f} pixels")
            print(f"     Precision@0.3: {eval_out.metrics['precision@0.3']:.4f}")
            print(f"     Precision@0.5: {eval_out.metrics['precision@0.5']:.4f}")
            print(f"     Precision@0.7: {eval_out.metrics['precision@0.7']:.4f}")
            print(f"     AUC: {eval_out.metrics['auc']:.4f}")

            results[tracker_type] = eval_out.metrics
        else:
            print(f"   ⚠ Evaluation failed: {eval_out.errors}")
    else:
        print(f"   ✗ Tracking failed: {tracker_out.errors}")

# Test with reinitialization on failure
print(f"\n{'='*60}")
print(f"3️⃣  Testing KCF with reinitialization...")
print(f"{'='*60}")

tracker_reinit = TrackerBlock('tracker_reinit')
tracker_reinit.configure(tracker_type='kcf', reinit_on_fail=True)
tracker_reinit_out = tracker_reinit.execute({
    'frames': data_out.data['frames'],
    'init_bbox': data_out.data['init_bbox']
})

if tracker_reinit_out.status.value == 'completed':
    print(f"   ✓ Tracking with reinit complete")
    print(f"     Success rate: {tracker_reinit_out.metrics['success_rate']:.2%}")
    print(f"     Failures: {tracker_reinit_out.metrics['n_failures']}")

    eval_reinit = CVEvaluationBlock('eval_reinit')
    eval_reinit.configure(metrics=['iou', 'center_error'])
    eval_reinit_out = eval_reinit.execute({
        'tracked_boxes': tracker_reinit_out.data['tracked_boxes'],
        'ground_truth': data_out.data['ground_truth']
    })

    if eval_reinit_out.status.value == 'completed':
        print(f"\n   📊 With Reinitialization:")
        print(f"     Avg IoU: {eval_reinit_out.metrics['avg_iou']:.4f}")
        print(f"     Avg Center Error: {eval_reinit_out.metrics['avg_center_error']:.2f} pixels")

# Summary
print(f"\n{'='*60}")
print("📊 Tracking Algorithm Comparison")
print(f"{'='*60}")

if results:
    print(f"\n{'Tracker':<15} {'Avg IoU':<12} {'Precision@0.5':<15} {'AUC':<10}")
    print("-" * 60)

    # Sort by Avg IoU
    sorted_results = sorted(results.items(), key=lambda x: x[1]['avg_iou'], reverse=True)

    for tracker, metrics in sorted_results:
        iou = metrics['avg_iou']
        prec = metrics['precision@0.5']
        auc = metrics['auc']
        print(f"{tracker.upper():<15} {iou:<12.4f} {prec:<15.4f} {auc:<10.4f}")

    # Determine best tracker
    best_tracker = sorted_results[0][0]
    best_iou = sorted_results[0][1]['avg_iou']

    print(f"\n🏆 Best Tracker: {best_tracker.upper()} (IoU: {best_iou:.4f})")

    print("\n📝 Tracker Characteristics:")
    print("  • KCF: Fast, good for simple scenarios")
    print("  • CSRT: Most accurate, slower")
    print("  • MOSSE: Very fast, lower accuracy")
    print("  • MIL: Moderate speed and accuracy")

print("\n✨ Tracking tests completed!")
