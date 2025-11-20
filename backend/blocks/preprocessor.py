"""Preprocessor Block - Data cleaning and transformation"""

import pandas as pd
import numpy as np
from typing import Any, Dict, List
from .base import BaseBlock, BlockOutput, BlockStatus


class PreprocessorBlock(BaseBlock):
    """Clean, normalize, and transform data"""

    def configure(self, **kwargs) -> None:
        self.config.update(kwargs)
        self.status = BlockStatus.CONFIGURED

    def validate_config(self) -> List[str]:
        return []

    def execute(self, inputs: Dict[str, Any]) -> BlockOutput:
        self.status = BlockStatus.RUNNING
        try:
            # Accept either dataframe or features
            data = inputs.get('dataframe') or inputs.get('features')
            if data is None:
                raise ValueError("Missing required input: dataframe or features")

            processed_data = data.copy()

            # Normalization
            if self.config.get('normalize', True):
                numeric_cols = processed_data.select_dtypes(include=[np.number]).columns
                for col in numeric_cols:
                    if col not in ['user_id', 'item_id', 'timestamp']:
                        processed_data[col] = (processed_data[col] - processed_data[col].mean()) / (processed_data[col].std() + 1e-8)

            # Handle missing values
            if self.config.get('fill_missing', True):
                processed_data = processed_data.fillna(processed_data.mean(numeric_only=True))

            self.status = BlockStatus.COMPLETED
            return BlockOutput(
                block_id=self.block_id,
                status=BlockStatus.COMPLETED,
                data={'processed-data': processed_data},
                metrics={
                    'n_rows': len(processed_data),
                    'n_features': len(processed_data.columns)
                }
            )
        except Exception as e:
            self.status = BlockStatus.FAILED
            return BlockOutput(block_id=self.block_id, status=BlockStatus.FAILED, errors=[str(e)])

    def get_schema(self) -> Dict[str, Any]:
        return {
            'type': 'preprocessor',
            'inputs': {'dataframe': {'type': 'DataFrame'}, 'features': {'type': 'DataFrame'}},
            'outputs': {'processed-data': {'type': 'DataFrame'}},
            'config': {
                'normalize': {'type': 'bool', 'default': True},
                'fill_missing': {'type': 'bool', 'default': True}
            }
        }
