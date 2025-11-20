"""Predictions Block - Generate recommendations"""

import numpy as np
from typing import Any, Dict, List
from .base import BaseBlock, BlockOutput, BlockStatus


class PredictionsBlock(BaseBlock):
    """Generate top-K recommendations for users"""

    def configure(self, **kwargs) -> None:
        self.config.update(kwargs)
        self.status = BlockStatus.CONFIGURED

    def validate_config(self) -> List[str]:
        return []

    def execute(self, inputs: Dict[str, Any]) -> BlockOutput:
        self.status = BlockStatus.RUNNING
        try:
            model = inputs.get('model')
            if not model:
                raise ValueError("Missing required input: model")

            top_k = self.config.get('top_k', 10)

            # Generate recommendations based on model predictions
            if 'predictions' in model:
                predictions_matrix = model['predictions']
                # Get top-k items for each user
                n_users = predictions_matrix.shape[0]
                recommendations = {}

                for user_idx in range(min(n_users, 100)):  # Limit for demo
                    user_predictions = predictions_matrix[user_idx]
                    if hasattr(user_predictions, 'toarray'):
                        user_predictions = user_predictions.toarray().flatten()
                    top_items = np.argsort(user_predictions)[-top_k:][::-1]
                    recommendations[user_idx] = [(int(item), float(user_predictions[item])) for item in top_items]
            else:
                # Placeholder recommendations
                recommendations = {0: [(i, 4.0) for i in range(top_k)]}

            self.status = BlockStatus.COMPLETED
            return BlockOutput(
                block_id=self.block_id,
                status=BlockStatus.COMPLETED,
                data={'recommendations': recommendations},
                metrics={
                    'n_users': len(recommendations),
                    'top_k': top_k
                }
            )
        except Exception as e:
            self.status = BlockStatus.FAILED
            return BlockOutput(block_id=self.block_id, status=BlockStatus.FAILED, errors=[str(e)])

    def get_schema(self) -> Dict[str, Any]:
        return {
            'type': 'predictions',
            'inputs': {'model': {'type': 'dict', 'required': True}},
            'outputs': {'recommendations': {'type': 'dict'}},
            'config': {
                'top_k': {'type': 'int', 'default': 10}
            }
        }
