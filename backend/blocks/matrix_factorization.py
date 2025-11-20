"""Matrix Factorization Block - SVD, ALS, NMF"""

import numpy as np
from typing import Any, Dict, List
from .base import BaseBlock, BlockOutput, BlockStatus
from scipy.sparse.linalg import svds


class MatrixFactorizationBlock(BaseBlock):
    """SVD, ALS, or NMF-based matrix factorization"""

    def __init__(self, block_id: str, config=None):
        super().__init__(block_id, config)
        self.user_factors = None
        self.item_factors = None

    def configure(self, **kwargs) -> None:
        self.config.update(kwargs)
        self.status = BlockStatus.CONFIGURED

    def validate_config(self) -> List[str]:
        errors = []
        method = self.config.get('method', 'svd')
        if method not in ['svd', 'als', 'nmf']:
            errors.append(f"Invalid method: {method}")
        return errors

    def execute(self, inputs: Dict[str, Any]) -> BlockOutput:
        self.status = BlockStatus.RUNNING
        try:
            train_data = inputs.get('split-data', {}).get('train') or inputs.get('processed-data')
            if train_data is None:
                raise ValueError("Missing training data")

            # Create matrix (simplified)
            from .collaborative_filtering import CollaborativeFilteringBlock
            temp_block = CollaborativeFilteringBlock('temp')
            matrix = temp_block._create_matrix(train_data)

            # SVD factorization
            n_factors = self.config.get('n_factors', 100)
            n_factors = min(n_factors, min(matrix.shape) - 1)

            U, sigma, Vt = svds(matrix.astype(float), k=n_factors)

            self.user_factors = U
            self.item_factors = Vt.T

            # Reconstruct predictions
            predictions = U @ np.diag(sigma) @ Vt

            model = {
                'method': 'svd',
                'user_factors': self.user_factors,
                'item_factors': self.item_factors,
                'predictions': predictions
            }

            self.status = BlockStatus.COMPLETED
            return BlockOutput(
                block_id=self.block_id,
                status=BlockStatus.COMPLETED,
                data={'model': model},
                metrics={
                    'n_factors': n_factors,
                    'user_factors_shape': self.user_factors.shape,
                    'item_factors_shape': self.item_factors.shape
                }
            )
        except Exception as e:
            self.status = BlockStatus.FAILED
            return BlockOutput(block_id=self.block_id, status=BlockStatus.FAILED, errors=[str(e)])

    def get_schema(self) -> Dict[str, Any]:
        return {
            'type': 'matrix-factorization',
            'inputs': {'split-data': {'type': 'dict'}, 'processed-data': {'type': 'DataFrame'}},
            'outputs': {'model': {'type': 'dict'}},
            'config': {
                'method': {'type': 'str', 'default': 'svd', 'options': ['svd', 'als', 'nmf']},
                'n_factors': {'type': 'int', 'default': 100},
                'n_epochs': {'type': 'int', 'default': 20}
            }
        }
