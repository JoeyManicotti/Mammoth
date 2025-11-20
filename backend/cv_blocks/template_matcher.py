"""Template Matching Block - Various template matching algorithms"""

import cv2
import numpy as np
from typing import Dict, Any, List
import logging

from backend.blocks.base import BaseBlock, BlockOutput, BlockStatus

logger = logging.getLogger(__name__)


class TemplateMatcherBlock(BaseBlock):
    """Template matching using various OpenCV methods"""

    METHODS = {
        'ccoeff': cv2.TM_CCOEFF,
        'ccoeff_normed': cv2.TM_CCOEFF_NORMED,
        'ccorr': cv2.TM_CCORR,
        'ccorr_normed': cv2.TM_CCORR_NORMED,
        'sqdiff': cv2.TM_SQDIFF,
        'sqdiff_normed': cv2.TM_SQDIFF_NORMED
    }

    def __init__(self, block_id: str, config=None):
        super().__init__(block_id, config)
        self.block_type = 'template-matcher'

    def configure(self, **kwargs):
        """Configure template matching parameters"""
        self.config.update(kwargs)
        self.status = BlockStatus.CONFIGURED

    def validate_config(self):
        """Validate template matching configuration"""
        errors = []
        method = self.config.get('method', 'ccoeff_normed')
        if method not in self.METHODS:
            errors.append(f"Invalid method: {method}")
        return errors

    def get_schema(self):
        """Get block schema"""
        return {
            'type': 'template-matcher',
            'inputs': {'frames': 'List[ndarray]', 'init_bbox': 'List[int]'},
            'outputs': {'tracked_boxes': 'List[List[int]]', 'match_scores': 'List[float]'}
        }

    def _error(self, message: str):
        """Helper to create error output"""
        return BlockOutput(block_id=self.block_id, status=BlockStatus.FAILED,
            errors=[message]
        )

    def execute(self, inputs: Dict[str, Any]) -> BlockOutput:
        """Perform template matching on video frames"""
        try:
            frames = inputs.get('frames')
            init_bbox = inputs.get('init_bbox')

            if frames is None:
                return self._error("No frames provided")
            if init_bbox is None:
                return self._error("No initial bounding box provided")

            method_name = self.config.get('method', 'ccoeff_normed')
            method = self.METHODS[method_name]
            update_template = self.config.get('update_template', False)
            update_freq = self.config.get('update_frequency', 10)

            # Extract initial template
            x, y, w, h = init_bbox
            template = frames[0][y:y+h, x:x+w]

            if template.size == 0:
                return self._error("Invalid initial bounding box")

            # Track object through frames
            tracked_boxes = []
            match_scores = []

            for frame_idx, frame in enumerate(frames):
                # Perform template matching
                result = cv2.matchTemplate(frame, template, method)

                # Find best match
                if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                    top_left = min_loc
                    score = 1.0 - min_val
                else:
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                    top_left = max_loc
                    score = max_val

                # Calculate bounding box
                x, y = top_left
                bbox = [x, y, w, h]
                tracked_boxes.append(bbox)
                match_scores.append(float(score))

                # Update template periodically if enabled
                if update_template and frame_idx % update_freq == 0 and frame_idx > 0:
                    x, y, w, h = bbox
                    if (x >= 0 and y >= 0 and x + w <= frame.shape[1] and y + h <= frame.shape[0]):
                        template = frame[y:y+h, x:x+w]

            return BlockOutput(
                block_id=self.block_id,
                status=BlockStatus.COMPLETED,
                data={
                    'tracked_boxes': tracked_boxes,
                    'match_scores': match_scores,
                    'template': template,
                    'frames': frames
                },
                metrics={
                    'method': method_name,
                    'n_frames': len(frames),
                    'avg_match_score': float(np.mean(match_scores)),
                    'min_match_score': float(np.min(match_scores)),
                    'max_match_score': float(np.max(match_scores)),
                    'template_updated': update_template
                }
            )

        except Exception as e:
            logger.error(f"Error in template matching: {e}")
            return self._error(str(e))
