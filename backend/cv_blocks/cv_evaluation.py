"""CV Evaluation Block - Metrics for tracking and template matching"""

import numpy as np
from typing import Dict, Any, List
import logging

from backend.blocks.base import BaseBlock, BlockOutput, BlockStatus

logger = logging.getLogger(__name__)


class CVEvaluationBlock(BaseBlock):
    """Evaluate tracking and template matching performance"""

    def __init__(self, block_id: str, config=None):
        super().__init__(block_id, config)
        self.block_type = 'cv-evaluation'

    def configure(self, **kwargs):
        """Configure evaluation parameters"""
        self.config.update(kwargs)
        self.status = BlockStatus.CONFIGURED

    def validate_config(self):
        """Validate evaluation configuration"""
        errors = []
        metrics = self.config.get('metrics', ['iou', 'center_error'])
        valid_metrics = ['iou', 'precision', 'recall', 'center_error', 'success_plot']
        for metric in metrics:
            if metric not in valid_metrics:
                errors.append(f"Invalid metric: {metric}")
        return errors

    def get_schema(self):
        """Get block schema"""
        return {
            'type': 'cv-evaluation',
            'inputs': {'tracked_boxes': 'List[List[int]]', 'ground_truth': 'List[Dict]'},
            'outputs': {'ious': 'List[float]', 'center_errors': 'List[float]'}
        }

    def _error(self, message: str):
        """Helper to create error output"""
        return BlockOutput(block_id=self.block_id, status=BlockStatus.FAILED,
            errors=[message]
        )

    def _calculate_iou(self, bbox1: List, bbox2: List) -> float:
        """Calculate Intersection over Union between two bounding boxes"""
        x1, y1, w1, h1 = bbox1
        x2, y2, w2, h2 = bbox2

        x_left = max(x1, x2)
        y_top = max(y1, y2)
        x_right = min(x1 + w1, x2 + w2)
        y_bottom = min(y1 + h1, y2 + h2)

        if x_right < x_left or y_bottom < y_top:
            return 0.0

        intersection_area = (x_right - x_left) * (y_bottom - y_top)
        bbox1_area = w1 * h1
        bbox2_area = w2 * h2
        union_area = bbox1_area + bbox2_area - intersection_area

        if union_area == 0:
            return 0.0

        return float(intersection_area / union_area)

    def _calculate_center_error(self, bbox1: List, bbox2: List) -> float:
        """Calculate Euclidean distance between bbox centers"""
        x1, y1, w1, h1 = bbox1
        x2, y2, w2, h2 = bbox2

        center1 = [x1 + w1/2, y1 + h1/2]
        center2 = [x2 + w2/2, y2 + h2/2]

        dx = center1[0] - center2[0]
        dy = center1[1] - center2[1]

        return float(np.sqrt(dx**2 + dy**2))

    def _compute_basic_stats(self, tracked_boxes: List) -> BlockOutput:
        """Compute basic statistics when no ground truth available"""
        if len(tracked_boxes) == 0:
            return self._error("No tracked boxes to evaluate")

        areas = []
        centers = []
        aspect_ratios = []

        for bbox in tracked_boxes:
            x, y, w, h = bbox
            area = w * h
            center = [x + w/2, y + h/2]
            aspect_ratio = w / h if h > 0 else 0

            areas.append(area)
            centers.append(center)
            aspect_ratios.append(aspect_ratio)

        displacements = []
        for i in range(1, len(centers)):
            dx = centers[i][0] - centers[i-1][0]
            dy = centers[i][1] - centers[i-1][1]
            displacement = np.sqrt(dx**2 + dy**2)
            displacements.append(displacement)

        results = {
            'n_frames': len(tracked_boxes),
            'avg_area': float(np.mean(areas)),
            'std_area': float(np.std(areas)),
            'avg_aspect_ratio': float(np.mean(aspect_ratios)),
            'avg_displacement': float(np.mean(displacements)) if displacements else 0.0,
            'max_displacement': float(np.max(displacements)) if displacements else 0.0,
            'total_distance': float(np.sum(displacements)) if displacements else 0.0
        }

        return BlockOutput(
            block_id=self.block_id,
            status=BlockStatus.COMPLETED,
            data={
                'tracked_boxes': tracked_boxes,
                'areas': areas,
                'centers': centers,
                'displacements': displacements
            },
            metrics=results
        )

    def execute(self, inputs: Dict[str, Any]) -> BlockOutput:
        """Evaluate tracking performance"""
        try:
            tracked_boxes = inputs.get('tracked_boxes')
            ground_truth = inputs.get('ground_truth')

            if tracked_boxes is None:
                return self._error("No tracked boxes provided")

            if ground_truth is None:
                return self._compute_basic_stats(tracked_boxes)

            metrics_to_compute = self.config.get('metrics', ['iou', 'center_error'])
            iou_thresholds = self.config.get('iou_thresholds', [0.3, 0.5, 0.7])

            results = {}
            ious = []
            center_errors = []

            n_frames = min(len(tracked_boxes), len(ground_truth))

            for i in range(n_frames):
                pred_bbox = tracked_boxes[i]
                if isinstance(ground_truth[i], dict):
                    gt_bbox = ground_truth[i]['bbox']
                else:
                    gt_bbox = ground_truth[i]

                iou = self._calculate_iou(pred_bbox, gt_bbox)
                ious.append(iou)

                center_error = self._calculate_center_error(pred_bbox, gt_bbox)
                center_errors.append(center_error)

            if 'iou' in metrics_to_compute:
                results['avg_iou'] = float(np.mean(ious))
                results['min_iou'] = float(np.min(ious))
                results['max_iou'] = float(np.max(ious))
                results['std_iou'] = float(np.std(ious))

            if 'center_error' in metrics_to_compute:
                results['avg_center_error'] = float(np.mean(center_errors))
                results['median_center_error'] = float(np.median(center_errors))
                results['max_center_error'] = float(np.max(center_errors))

            if 'precision' in metrics_to_compute:
                for threshold in iou_thresholds:
                    success_count = sum(1 for iou in ious if iou >= threshold)
                    precision = success_count / len(ious) if len(ious) > 0 else 0.0
                    results[f'precision@{threshold}'] = float(precision)

            if 'success_plot' in metrics_to_compute:
                thresholds = np.linspace(0, 1, 21)
                success_rates = []
                for threshold in thresholds:
                    success_count = sum(1 for iou in ious if iou >= threshold)
                    success_rate = success_count / len(ious) if len(ious) > 0 else 0.0
                    success_rates.append(success_rate)

                results['success_plot_thresholds'] = thresholds.tolist()
                results['success_plot_rates'] = success_rates
                results['auc'] = float(np.mean(success_rates))

            if 'recall' in metrics_to_compute:
                recall_count = sum(1 for iou in ious if iou > 0)
                results['recall'] = float(recall_count / len(ious)) if len(ious) > 0 else 0.0

            return BlockOutput(
                block_id=self.block_id,
                status=BlockStatus.COMPLETED,
                data={
                    'ious': ious,
                    'center_errors': center_errors,
                    'tracked_boxes': tracked_boxes,
                    'ground_truth': ground_truth
                },
                metrics=results
            )

        except Exception as e:
            logger.error(f"Error in CV evaluation: {e}")
            return self._error(str(e))
