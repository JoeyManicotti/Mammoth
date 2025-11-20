"""Split Block - Train/test data splitting"""

import pandas as pd
from typing import Any, Dict, List
from .base import BaseBlock, BlockOutput, BlockStatus
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.data_loader import DataLoader


class SplitBlock(BaseBlock):
    """Split data into training and test sets"""

    def __init__(self, block_id: str, config=None):
        super().__init__(block_id, config)
        self.loader = DataLoader()

    def configure(self, **kwargs) -> None:
        self.config.update(kwargs)
        self.status = BlockStatus.CONFIGURED

    def validate_config(self) -> List[str]:
        errors = []
        test_size = self.config.get('test_size', 0.2)
        if not 0 < test_size < 1:
            errors.append(f"test_size must be between 0 and 1, got {test_size}")
        return errors

    def execute(self, inputs: Dict[str, Any]) -> BlockOutput:
        self.status = BlockStatus.RUNNING
        try:
            if 'dataframe' not in inputs:
                raise ValueError("Missing required input: dataframe")

            data = inputs['dataframe']
            test_size = self.config.get('test_size', 0.2)
            split_method = self.config.get('method', 'random')

            if split_method == 'temporal':
                train_data, test_data = self.loader.temporal_split(data, test_size)
            else:
                train_data, test_data = self.loader.train_test_split(data, test_size)

            self.status = BlockStatus.COMPLETED
            return BlockOutput(
                block_id=self.block_id,
                status=BlockStatus.COMPLETED,
                data={
                    'train_data': train_data,
                    'test_data': test_data,
                    'split-data': {'train': train_data, 'test': test_data}
                },
                metrics={
                    'train_size': len(train_data),
                    'test_size': len(test_data),
                    'split_ratio': len(test_data) / len(data)
                }
            )
        except Exception as e:
            self.status = BlockStatus.FAILED
            return BlockOutput(block_id=self.block_id, status=BlockStatus.FAILED, errors=[str(e)])

    def get_schema(self) -> Dict[str, Any]:
        return {
            'type': 'split',
            'inputs': {'dataframe': {'type': 'DataFrame', 'required': True}},
            'outputs': {'train_data': {'type': 'DataFrame'}, 'test_data': {'type': 'DataFrame'}},
            'config': {
                'test_size': {'type': 'float', 'default': 0.2},
                'method': {'type': 'str', 'default': 'random', 'options': ['random', 'temporal']}
            }
        }
