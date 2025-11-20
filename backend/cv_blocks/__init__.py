"""
Mammoth Computer Vision Blocks

Standardized module system for building and testing CV pipelines.
Each block implements a specific functionality in the CV workflow.
"""

from backend.blocks.base import BaseBlock, BlockConfig, BlockOutput, BlockStatus
from .cv_data_source import CVDataSourceBlock
from .template_matcher import TemplateMatcherBlock
from .feature_matcher import FeatureMatcherBlock
from .tracker import TrackerBlock
from .cv_evaluation import CVEvaluationBlock

__all__ = [
    'BaseBlock',
    'BlockConfig',
    'BlockOutput',
    'BlockStatus',
    'CVDataSourceBlock',
    'TemplateMatcherBlock',
    'FeatureMatcherBlock',
    'TrackerBlock',
    'CVEvaluationBlock'
]
