"""Collaborative Filtering Block"""

import pandas as pd
import numpy as np
from typing import Any, Dict, List
from .base import BaseBlock, BlockOutput, BlockStatus
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity


class CollaborativeFilteringBlock(BaseBlock):
    """User-based or item-based collaborative filtering"""

    def __init__(self, block_id: str, config=None):
        super().__init__(block_id, config)
        self.model = None
        self.similarity_matrix = None

    def configure(self, **kwargs) -> None:
        self.config.update(kwargs)
        self.status = BlockStatus.CONFIGURED

    def validate_config(self) -> List[str]:
        errors = []
        method = self.config.get('method', 'user-based')
        if method not in ['user-based', 'item-based']:
            errors.append(f"Invalid method: {method}")
        return errors

    def execute(self, inputs: Dict[str, Any]) -> BlockOutput:
        self.status = BlockStatus.RUNNING
        try:
            # Get training data
            train_data = inputs.get('split-data', {}).get('train') or inputs.get('processed-data')
            if train_data is None:
                raise ValueError("Missing training data")

            # Create interaction matrix
            matrix = self._create_matrix(train_data)

            # Compute similarity
            method = self.config.get('method', 'user-based')
            if method == 'user-based':
                self.similarity_matrix = cosine_similarity(matrix)
            else:
                self.similarity_matrix = cosine_similarity(matrix.T)

            # Simple prediction: matrix multiplication
            if method == 'user-based':
                predictions = self.similarity_matrix @ matrix
            else:
                predictions = matrix @ self.similarity_matrix

            self.model = {'method': method, 'matrix': matrix, 'predictions': predictions}

            self.status = BlockStatus.COMPLETED
            return BlockOutput(
                block_id=self.block_id,
                status=BlockStatus.COMPLETED,
                data={'model': self.model},
                metrics={
                    'method': method,
                    'matrix_shape': matrix.shape,
                    'sparsity': 1 - matrix.nnz / (matrix.shape[0] * matrix.shape[1])
                }
            )
        except Exception as e:
            self.status = BlockStatus.FAILED
            return BlockOutput(block_id=self.block_id, status=BlockStatus.FAILED, errors=[str(e)])

    def _create_matrix(self, data: pd.DataFrame):
        """Create user-item interaction matrix"""
        user_ids = data['user_id'].unique()
        item_ids = data['item_id'].unique()

        user_map = {uid: idx for idx, uid in enumerate(user_ids)}
        item_map = {iid: idx for idx, iid in enumerate(item_ids)}

        rows = [user_map[uid] for uid in data['user_id']]
        cols = [item_map[iid] for iid in data['item_id']]
        vals = data['rating'].values

        return csr_matrix((vals, (rows, cols)), shape=(len(user_ids), len(item_ids)))

    def get_schema(self) -> Dict[str, Any]:
        return {
            'type': 'collaborative-filtering',
            'inputs': {'split-data': {'type': 'dict'}, 'processed-data': {'type': 'DataFrame'}},
            'outputs': {'model': {'type': 'dict'}},
            'config': {
                'method': {'type': 'str', 'default': 'user-based', 'options': ['user-based', 'item-based']},
                'k_neighbors': {'type': 'int', 'default': 50}
            }
        }
