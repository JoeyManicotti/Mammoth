"""Features Input Block - User/item metadata and features"""

import pandas as pd
from typing import Any, Dict, List, Optional
from .base import BaseBlock, BlockOutput, BlockStatus


class FeaturesInputBlock(BaseBlock):
    """Load and provide user/item features"""

    def configure(self, **kwargs) -> None:
        self.config.update(kwargs)
        self.status = BlockStatus.CONFIGURED

    def validate_config(self) -> List[str]:
        errors = []
        if not self.config.get('feature_type'):
            errors.append("Missing feature_type (user/item)")
        return errors

    def execute(self, inputs: Dict[str, Any]) -> BlockOutput:
        self.status = BlockStatus.RUNNING
        try:
            # Create placeholder features
            feature_type = self.config['feature_type']
            n_entities = self.config.get('n_entities', 100)

            features = pd.DataFrame({
                f'{feature_type}_id': range(n_entities),
                'feature_1': range(n_entities),
                'feature_2': range(n_entities)
            })

            self.status = BlockStatus.COMPLETED
            return BlockOutput(
                block_id=self.block_id,
                status=BlockStatus.COMPLETED,
                data={'features': features},
                metrics={'n_features': len(features.columns) - 1}
            )
        except Exception as e:
            self.status = BlockStatus.FAILED
            return BlockOutput(block_id=self.block_id, status=BlockStatus.FAILED, errors=[str(e)])

    def get_schema(self) -> Dict[str, Any]:
        return {
            'type': 'features-input',
            'inputs': {},
            'outputs': {'features': {'type': 'DataFrame'}},
            'config': {
                'feature_type': {'type': 'str', 'required': True, 'options': ['user', 'item']},
                'n_entities': {'type': 'int', 'default': 100}
            }
        }
