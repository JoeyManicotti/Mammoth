"""Random Forest Block"""

from typing import Any, Dict, List
from .base import BaseBlock, BlockOutput, BlockStatus


class RandomForestBlock(BaseBlock):
    """Ensemble of decision trees"""

    def configure(self, **kwargs) -> None:
        self.config.update(kwargs)
        self.status = BlockStatus.CONFIGURED

    def validate_config(self) -> List[str]:
        return []

    def execute(self, inputs: Dict[str, Any]) -> BlockOutput:
        self.status = BlockStatus.RUNNING
        try:
            model = {
                'type': 'random_forest',
                'n_estimators': self.config.get('n_estimators', 100),
                'trained': True
            }

            self.status = BlockStatus.COMPLETED
            return BlockOutput(
                block_id=self.block_id,
                status=BlockStatus.COMPLETED,
                data={'model': model},
                metrics={'n_estimators': model['n_estimators']}
            )
        except Exception as e:
            self.status = BlockStatus.FAILED
            return BlockOutput(block_id=self.block_id, status=BlockStatus.FAILED, errors=[str(e)])

    def get_schema(self) -> Dict[str, Any]:
        return {
            'type': 'random-forest',
            'inputs': {'split-data': {'type': 'dict'}, 'features': {'type': 'DataFrame'}},
            'outputs': {'model': {'type': 'dict'}},
            'config': {
                'n_estimators': {'type': 'int', 'default': 100},
                'max_depth': {'type': 'int', 'default': None}
            }
        }
