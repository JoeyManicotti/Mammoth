"""
Mammoth Recommender System Blocks

Standardized module system for building and testing recommender pipelines.
Each block implements a specific functionality in the recommendation workflow.
"""

from .base import BaseBlock, BlockConfig, BlockOutput, BlockStatus
from .data_source import DataSourceBlock
from .features_input import FeaturesInputBlock
from .split import SplitBlock
from .preprocessor import PreprocessorBlock
from .collaborative_filtering import CollaborativeFilteringBlock
from .matrix_factorization import MatrixFactorizationBlock
from .xgboost_block import XGBoostBlock
from .random_forest import RandomForestBlock
from .deep_learning import DeepLearningBlock
from .predictions import PredictionsBlock
from .evaluation import EvaluationBlock

__all__ = [
    'BaseBlock',
    'BlockConfig',
    'BlockOutput',
    'BlockStatus',
    'DataSourceBlock',
    'FeaturesInputBlock',
    'SplitBlock',
    'PreprocessorBlock',
    'CollaborativeFilteringBlock',
    'MatrixFactorizationBlock',
    'XGBoostBlock',
    'RandomForestBlock',
    'DeepLearningBlock',
    'PredictionsBlock',
    'EvaluationBlock'
]
