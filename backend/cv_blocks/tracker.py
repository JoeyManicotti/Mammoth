"""Tracker Block - Object tracking algorithms"""

import cv2
import numpy as np
from typing import Dict, Any, List
import logging

from backend.blocks.base import BaseBlock, BlockOutput, BlockStatus

logger = logging.getLogger(__name__)


class TrackerBlock(BaseBlock):
    """Object tracking using various OpenCV trackers"""

    def __init__(self, block_id: str, config=None):
        super().__init__(block_id, config)
        self.block_type = 'tracker'

    def configure(self, **kwargs):
        """Configure tracker parameters"""
        self.config.update(kwargs)
        self.status = BlockStatus.CONFIGURED

    def validate_config(self):
        """Validate tracker configuration"""
        errors = []
        tracker_type = self.config.get('tracker_type', 'kcf')
        if tracker_type not in ['kcf', 'csrt', 'medianflow', 'mosse', 'mil', 'boosting', 'tld']:
            errors.append(f"Invalid tracker: {tracker_type}")
        return errors

    def get_schema(self):
        """Get block schema"""
        return {
            'type': 'tracker',
            'inputs': {'frames': 'List[ndarray]', 'init_bbox': 'List[int]'},
            'outputs': {'tracked_boxes': 'List[List[int]]', 'confidence_scores': 'List[float]'}
        }

    def _error(self, message: str):
        """Helper to create error output"""
        return BlockOutput(block_id=self.block_id, status=BlockStatus.FAILED,
            errors=[message]
        )

    def _create_tracker(self, tracker_type: str):
        """Create OpenCV tracker based on type"""
        try:
            if tracker_type == 'kcf':
                return cv2.legacy.TrackerKCF_create()
            elif tracker_type == 'csrt':
                return cv2.legacy.TrackerCSRT_create()
            elif tracker_type == 'medianflow':
                return cv2.legacy.TrackerMedianFlow_create()
            elif tracker_type == 'mosse':
                return cv2.legacy.TrackerMOSSE_create()
            elif tracker_type == 'mil':
                return cv2.legacy.TrackerMIL_create()
            elif tracker_type == 'boosting':
                return cv2.legacy.TrackerBoosting_create()
            elif tracker_type == 'tld':
                return cv2.legacy.TrackerTLD_create()
            else:
                logger.warning(f"Unknown tracker type: {tracker_type}, using KCF")
                return cv2.legacy.TrackerKCF_create()
        except AttributeError:
            try:
                if tracker_type == 'kcf':
                    return cv2.TrackerKCF_create()
                elif tracker_type == 'csrt':
                    return cv2.TrackerCSRT_create()
                elif tracker_type == 'mil':
                    return cv2.TrackerMIL_create()
                elif tracker_type == 'mosse':
                    return cv2.TrackerMOSSE_create()
                else:
                    logger.error(f"Tracker {tracker_type} not available")
                    return None
            except Exception as e:
                logger.error(f"Could not create tracker: {e}")
                return None

    def execute(self, inputs: Dict[str, Any]) -> BlockOutput:
        """Perform object tracking"""
        try:
            frames = inputs.get('frames')
            init_bbox = inputs.get('init_bbox')

            if frames is None:
                return self._error("No frames provided")
            if init_bbox is None:
                return self._error("No initial bounding box provided")

            tracker_type = self.config.get('tracker_type', 'kcf')
            reinit_on_fail = self.config.get('reinit_on_fail', False)

            # Create tracker
            tracker = self._create_tracker(tracker_type)
            if tracker is None:
                return self._error(f"Could not create tracker: {tracker_type}")

            # Initialize tracker on first frame
            x, y, w, h = init_bbox
            bbox = (x, y, w, h)

            success = tracker.init(frames[0], bbox)
            if not success:
                return self._error("Failed to initialize tracker")

            # Track through frames
            tracked_boxes = [init_bbox]
            tracking_success = [True]
            confidence_scores = [1.0]

            for frame_idx in range(1, len(frames)):
                frame = frames[frame_idx]
                success, bbox = tracker.update(frame)

                if success:
                    x, y, w, h = bbox
                    x = max(0, int(x))
                    y = max(0, int(y))
                    w = max(1, int(w))
                    h = max(1, int(h))

                    if x + w > frame.shape[1]:
                        w = frame.shape[1] - x
                    if y + h > frame.shape[0]:
                        h = frame.shape[0] - y

                    tracked_boxes.append([x, y, w, h])
                    tracking_success.append(True)

                    if len(tracked_boxes) > 1:
                        prev_area = tracked_boxes[-2][2] * tracked_boxes[-2][3]
                        curr_area = w * h
                        area_ratio = min(curr_area, prev_area) / max(curr_area, prev_area)
                        confidence = area_ratio
                    else:
                        confidence = 1.0

                    confidence_scores.append(confidence)
                else:
                    if reinit_on_fail and len(tracked_boxes) > 0:
                        tracked_boxes.append(tracked_boxes[-1])
                        tracking_success.append(False)
                        confidence_scores.append(0.0)
                    else:
                        tracked_boxes.append(tracked_boxes[-1] if tracked_boxes else init_bbox)
                        tracking_success.append(False)
                        confidence_scores.append(0.0)

            success_rate = sum(tracking_success) / len(tracking_success)

            return BlockOutput(
                block_id=self.block_id,
                status=BlockStatus.COMPLETED,
                data={
                    'tracked_boxes': tracked_boxes,
                    'tracking_success': tracking_success,
                    'confidence_scores': confidence_scores,
                    'frames': frames
                },
                metrics={
                    'tracker_type': tracker_type,
                    'n_frames': len(frames),
                    'success_rate': success_rate,
                    'avg_confidence': float(np.mean(confidence_scores)),
                    'n_failures': len(tracking_success) - sum(tracking_success)
                }
            )

        except Exception as e:
            logger.error(f"Error in tracking: {e}")
            return self._error(str(e))
