"""
Data Source Block

Loads user-item interaction data from various sources.
"""

import pandas as pd
import numpy as np
from typing import Any, Dict, List, Optional
from .base import BaseBlock, BlockOutput, BlockStatus
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from utils.data_loader import DataLoader


class DataSourceBlock(BaseBlock):
    """
    Load and provide raw data for the recommendation system

    Supported sources:
    - CSV files
    - Synthetic data generation
    - Database connections (future)
    - API endpoints (future)
    """

    def __init__(self, block_id: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(block_id, config)
        self.data_loader = DataLoader()
        self.data: Optional[pd.DataFrame] = None

    def configure(self, **kwargs) -> None:
        """
        Configure data source parameters

        Parameters:
            data_source: str - Type of data source ('csv', 'synthetic', 'database', 'api')
            file_path: str - Path to data file (for CSV)
            sample_size: int - Number of rows to load (0 for all)
            n_users: int - Number of users (for synthetic)
            n_items: int - Number of items (for synthetic)
            n_interactions: int - Number of interactions (for synthetic)
        """
        self.config.update(kwargs)
        self.status = BlockStatus.CONFIGURED
        self.logger.info(f"Configured {self.block_id} with source: {self.config.get('data_source', 'unknown')}")

    def validate_config(self) -> List[str]:
        """Validate configuration"""
        errors = []

        data_source = self.config.get('data_source')
        if not data_source:
            errors.append("Missing required parameter: data_source")
        elif data_source not in ['csv', 'synthetic', 'database', 'api']:
            errors.append(f"Invalid data_source: {data_source}")

        if data_source == 'csv':
            if not self.config.get('file_path'):
                errors.append("CSV source requires file_path parameter")

        return errors

    def execute(self, inputs: Dict[str, Any]) -> BlockOutput:
        """
        Load data from the configured source

        Args:
            inputs: Empty dict (source blocks don't need inputs)

        Returns:
            BlockOutput with 'dataframe' containing loaded data
        """
        self.status = BlockStatus.RUNNING
        self.logger.info(f"Executing {self.block_id}")

        try:
            errors = self.validate_config()
            if errors:
                self.status = BlockStatus.FAILED
                return BlockOutput(
                    block_id=self.block_id,
                    status=BlockStatus.FAILED,
                    errors=errors
                )

            data_source = self.config['data_source']

            if data_source == 'synthetic':
                self.data = self._load_synthetic()
            elif data_source == 'csv':
                self.data = self._load_csv()
            else:
                raise NotImplementedError(f"Data source '{data_source}' not yet implemented")

            # Apply sampling if requested
            sample_size = self.config.get('sample_size', 0)
            if sample_size > 0 and len(self.data) > sample_size:
                self.data = self.data.sample(n=sample_size, random_state=42)
                self.logger.info(f"Sampled {sample_size} rows")

            self.status = BlockStatus.COMPLETED
            self.output = BlockOutput(
                block_id=self.block_id,
                status=BlockStatus.COMPLETED,
                data={'dataframe': self.data},
                metrics={
                    'n_rows': len(self.data),
                    'n_users': self.data['user_id'].nunique(),
                    'n_items': self.data['item_id'].nunique(),
                    'sparsity': 1 - len(self.data) / (self.data['user_id'].nunique() * self.data['item_id'].nunique())
                }
            )

            self.logger.info(f"Loaded {len(self.data)} interactions")
            return self.output

        except Exception as e:
            self.status = BlockStatus.FAILED
            self.logger.error(f"Failed to load data: {str(e)}")
            return BlockOutput(
                block_id=self.block_id,
                status=BlockStatus.FAILED,
                errors=[str(e)]
            )

    def _load_synthetic(self) -> pd.DataFrame:
        """Generate synthetic data"""
        return self.data_loader.generate_synthetic(
            n_users=self.config.get('n_users', 100),
            n_items=self.config.get('n_items', 200),
            n_interactions=self.config.get('n_interactions', 1000)
        )

    def _load_csv(self) -> pd.DataFrame:
        """Load data from CSV file"""
        file_path = self.config['file_path']

        # Try to load with various formats
        try:
            data = pd.read_csv(file_path, sep='\t')
        except:
            data = pd.read_csv(file_path)

        # Ensure required columns exist
        required_cols = ['user_id', 'item_id', 'rating']
        if not all(col in data.columns for col in required_cols):
            # Try to infer column names
            if len(data.columns) >= 3:
                data.columns = ['user_id', 'item_id', 'rating', 'timestamp'] if len(data.columns) >= 4 else ['user_id', 'item_id', 'rating']
            else:
                raise ValueError(f"CSV must have columns: {required_cols}")

        if 'timestamp' not in data.columns:
            data['timestamp'] = np.arange(len(data))

        return data

    def get_schema(self) -> Dict[str, Any]:
        """Get block schema"""
        return {
            'type': 'data-source',
            'inputs': {},
            'outputs': {
                'dataframe': {
                    'type': 'DataFrame',
                    'schema': {
                        'user_id': 'int',
                        'item_id': 'int',
                        'rating': 'float',
                        'timestamp': 'int/datetime'
                    }
                }
            },
            'config': {
                'data_source': {'type': 'str', 'required': True, 'options': ['csv', 'synthetic', 'database', 'api']},
                'file_path': {'type': 'str', 'required_if': {'data_source': 'csv'}},
                'sample_size': {'type': 'int', 'default': 0},
                'n_users': {'type': 'int', 'default': 100},
                'n_items': {'type': 'int', 'default': 200},
                'n_interactions': {'type': 'int', 'default': 1000}
            }
        }
