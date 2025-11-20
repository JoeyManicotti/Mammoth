"""Feature Matching Block - Feature-based template matching"""

import cv2
import numpy as np
from typing import Dict, Any, List
import logging

from backend.blocks.base import BaseBlock, BlockOutput, BlockStatus

logger = logging.getLogger(__name__)


class FeatureMatcherBlock(BaseBlock):
    """Feature-based template matching using keypoint descriptors"""

    def __init__(self, block_id: str, config=None):
        super().__init__(block_id, config)
        self.block_type = 'feature-matcher'

    def configure(self, **kwargs):
        """Configure feature matching parameters"""
        self.config.update(kwargs)
        self.status = BlockStatus.CONFIGURED

    def validate_config(self):
        """Validate feature matching configuration"""
        errors = []
        method = self.config.get('method', 'orb')
        if method not in ['orb', 'akaze', 'brisk', 'sift']:
            errors.append(f"Invalid method: {method}")
        return errors

    def get_schema(self):
        """Get block schema"""
        return {
            'type': 'feature-matcher',
            'inputs': {'frames': 'List[ndarray]', 'init_bbox': 'List[int]'},
            'outputs': {'tracked_boxes': 'List[List[int]]', 'confidence_scores': 'List[float]'}
        }

    def _error(self, message: str):
        """Helper to create error output"""
        return BlockOutput(block_id=self.block_id, status=BlockStatus.FAILED,
            errors=[message]
        )

    def _create_detector(self, method: str):
        """Create feature detector based on method"""
        if method == 'orb':
            return cv2.ORB_create()
        elif method == 'akaze':
            return cv2.AKAZE_create()
        elif method == 'brisk':
            return cv2.BRISK_create()
        elif method == 'sift':
            try:
                return cv2.SIFT_create()
            except AttributeError:
                logger.warning("SIFT not available, using ORB instead")
                return cv2.ORB_create()
        else:
            return cv2.ORB_create()

    def execute(self, inputs: Dict[str, Any]) -> BlockOutput:
        """Perform feature-based template matching"""
        try:
            frames = inputs.get('frames')
            init_bbox = inputs.get('init_bbox')

            if frames is None:
                return self._error("No frames provided")
            if init_bbox is None:
                return self._error("No initial bounding box provided")

            method = self.config.get('method', 'orb')
            min_matches = self.config.get('min_matches', 10)
            ratio_thresh = self.config.get('ratio_threshold', 0.75)

            # Create feature detector
            detector = self._create_detector(method)

            # Extract initial template
            x, y, w, h = init_bbox
            template = frames[0][y:y+h, x:x+w]
            template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

            # Detect keypoints and compute descriptors for template
            kp_template, des_template = detector.detectAndCompute(template_gray, None)

            if des_template is None or len(kp_template) < min_matches:
                return self._error(f"Insufficient keypoints in template: {len(kp_template) if kp_template else 0}")

            # Create matcher
            if method in ['orb', 'akaze', 'brisk']:
                matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
            else:
                matcher = cv2.BFMatcher(cv2.NORM_L2, crossCheck=False)

            # Track through frames
            tracked_boxes = []
            match_counts = []
            confidence_scores = []

            for frame_idx, frame in enumerate(frames):
                frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                kp_frame, des_frame = detector.detectAndCompute(frame_gray, None)

                if des_frame is None or len(kp_frame) < min_matches:
                    if len(tracked_boxes) > 0:
                        tracked_boxes.append(tracked_boxes[-1])
                    else:
                        tracked_boxes.append(init_bbox)
                    match_counts.append(0)
                    confidence_scores.append(0.0)
                    continue

                # Match descriptors
                matches = matcher.knnMatch(des_template, des_frame, k=2)

                # Apply ratio test
                good_matches = []
                for match_pair in matches:
                    if len(match_pair) == 2:
                        m, n = match_pair
                        if m.distance < ratio_thresh * n.distance:
                            good_matches.append(m)

                match_counts.append(len(good_matches))

                if len(good_matches) >= min_matches:
                    src_pts = np.float32([kp_template[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
                    dst_pts = np.float32([kp_frame[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

                    H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

                    if H is not None:
                        h_t, w_t = template.shape[:2]
                        template_corners = np.float32([[0, 0], [w_t, 0], [w_t, h_t], [0, h_t]]).reshape(-1, 1, 2)
                        frame_corners = cv2.perspectiveTransform(template_corners, H)

                        x_min = int(np.min(frame_corners[:, 0, 0]))
                        y_min = int(np.min(frame_corners[:, 0, 1]))
                        x_max = int(np.max(frame_corners[:, 0, 0]))
                        y_max = int(np.max(frame_corners[:, 0, 1]))

                        x_min = max(0, x_min)
                        y_min = max(0, y_min)
                        x_max = min(frame.shape[1], x_max)
                        y_max = min(frame.shape[0], y_max)

                        bbox = [x_min, y_min, x_max - x_min, y_max - y_min]
                        confidence = len(good_matches) / len(kp_template)
                    else:
                        bbox = tracked_boxes[-1] if len(tracked_boxes) > 0 else init_bbox
                        confidence = 0.5
                else:
                    bbox = tracked_boxes[-1] if len(tracked_boxes) > 0 else init_bbox
                    confidence = len(good_matches) / min_matches if min_matches > 0 else 0.0

                tracked_boxes.append(bbox)
                confidence_scores.append(float(confidence))

            return BlockOutput(
                block_id=self.block_id,
                status=BlockStatus.COMPLETED,
                data={
                    'tracked_boxes': tracked_boxes,
                    'match_counts': match_counts,
                    'confidence_scores': confidence_scores,
                    'template': template,
                    'frames': frames
                },
                metrics={
                    'method': method,
                    'n_frames': len(frames),
                    'n_template_keypoints': len(kp_template),
                    'avg_matches': float(np.mean(match_counts)),
                    'avg_confidence': float(np.mean(confidence_scores)),
                    'min_matches_threshold': min_matches
                }
            )

        except Exception as e:
            logger.error(f"Error in feature matching: {e}")
            return self._error(str(e))
