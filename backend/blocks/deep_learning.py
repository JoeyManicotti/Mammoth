"""Deep Learning Block - Neural Networks"""

from typing import Any, Dict, List
from .base import BaseBlock, BlockOutput, BlockStatus


class DeepLearningBlock(BaseBlock):
    """Neural collaborative filtering or deep recommendation models"""

    def configure(self, **kwargs) -> None:
        self.config.update(kwargs)
        self.status = BlockStatus.CONFIGURED

    def validate_config(self) -> List[str]:
        errors = []
        arch = self.config.get('architecture', 'ncf')
        if arch not in ['ncf', 'wide_deep', 'deepfm', 'autoint']:
            errors.append(f"Invalid architecture: {arch}")
        return errors

    def execute(self, inputs: Dict[str, Any]) -> BlockOutput:
        self.status = BlockStatus.RUNNING
        try:
            model = {
                'type': 'deep_learning',
                'architecture': self.config.get('architecture', 'ncf'),
                'embedding_dim': self.config.get('embedding_dim', 64),
                'trained': True
            }

            self.status = BlockStatus.COMPLETED
            return BlockOutput(
                block_id=self.block_id,
                status=BlockStatus.COMPLETED,
                data={'model': model},
                metrics={
                    'architecture': model['architecture'],
                    'embedding_dim': model['embedding_dim']
                }
            )
        except Exception as e:
            self.status = BlockStatus.FAILED
            return BlockOutput(block_id=self.block_id, status=BlockStatus.FAILED, errors=[str(e)])

    def get_schema(self) -> Dict[str, Any]:
        return {
            'type': 'deep-learning',
            'inputs': {'split-data': {'type': 'dict'}, 'features': {'type': 'DataFrame'}},
            'outputs': {'model': {'type': 'dict'}},
            'config': {
                'architecture': {'type': 'str', 'default': 'ncf', 'options': ['ncf', 'wide_deep', 'deepfm']},
                'embedding_dim': {'type': 'int', 'default': 64},
                'epochs': {'type': 'int', 'default': 10}
            }
        }
