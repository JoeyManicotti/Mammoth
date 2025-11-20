"""Random Forest Block - Ensemble Learning for Recommendations"""

import numpy as np
import pandas as pd
from typing import Any, Dict, List
from .base import BaseBlock, BlockOutput, BlockStatus

try:
    from sklearn.ensemble import RandomForestRegressor
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class RandomForestBlock(BaseBlock):
    """Random Forest ensemble for rating prediction

    Uses scikit-learn's RandomForestRegressor for recommendation tasks.
    Similar to XGBoost but with different ensemble methodology.
    """

    def __init__(self, block_id: str, config=None):
        super().__init__(block_id, config)
        self.model = None
        self.user_ids = None
        self.item_ids = None
        self.user_map = None
        self.item_map = None

    def configure(self, **kwargs) -> None:
        self.config.update(kwargs)
        self.status = BlockStatus.CONFIGURED

    def validate_config(self) -> List[str]:
        errors = []
        if not SKLEARN_AVAILABLE:
            errors.append("scikit-learn not installed. Install with: pip install scikit-learn")

        n_estimators = self.config.get('n_estimators', 100)
        if n_estimators < 1:
            errors.append("n_estimators must be >= 1")

        max_depth = self.config.get('max_depth')
        if max_depth is not None and max_depth < 1:
            errors.append("max_depth must be >= 1 or None")

        return errors

    def execute(self, inputs: Dict[str, Any]) -> BlockOutput:
        self.status = BlockStatus.RUNNING
        try:
            if not SKLEARN_AVAILABLE:
                raise ImportError("scikit-learn not installed")

            # Get training data
            split_data = inputs.get('split-data', {})
            if split_data and 'train' in split_data:
                train_data = split_data['train']
            else:
                train_data = inputs.get('processed-data')

            if train_data is None:
                raise ValueError("Missing training data")

            # Create user and item mappings
            self.user_ids = sorted(train_data['user_id'].unique())
            self.item_ids = sorted(train_data['item_id'].unique())
            self.user_map = {uid: idx for idx, uid in enumerate(self.user_ids)}
            self.item_map = {iid: idx for idx, iid in enumerate(self.item_ids)}

            # Build feature matrix
            X_train, y_train = self._create_features(train_data)

            # Configure Random Forest
            params = {
                'n_estimators': self.config.get('n_estimators', 100),
                'max_depth': self.config.get('max_depth'),
                'min_samples_split': self.config.get('min_samples_split', 2),
                'min_samples_leaf': self.config.get('min_samples_leaf', 1),
                'max_features': self.config.get('max_features', 'sqrt'),
                'random_state': self.config.get('random_state', 42),
                'n_jobs': -1
            }

            # Train model
            self.model = RandomForestRegressor(**params)
            self.model.fit(X_train, y_train)

            # Generate predictions matrix
            predictions = self._generate_predictions_matrix()

            # Get feature importance
            feature_importance = self.model.feature_importances_
            top_features = np.argsort(feature_importance)[-5:][::-1]

            model_data = {
                'type': 'random_forest',
                'rf_model': self.model,
                'predictions': predictions,
                'user_map': self.user_map,
                'item_map': self.item_map,
                'feature_importance': feature_importance.tolist()
            }

            self.status = BlockStatus.COMPLETED
            return BlockOutput(
                block_id=self.block_id,
                status=BlockStatus.COMPLETED,
                data={'model': model_data},
                metrics={
                    'n_estimators': params['n_estimators'],
                    'max_depth': params['max_depth'] or 'None',
                    'n_users': len(self.user_ids),
                    'n_items': len(self.item_ids),
                    'n_training_samples': len(X_train),
                    'n_features': X_train.shape[1],
                    'predictions_shape': predictions.shape,
                    'top_feature_indices': top_features.tolist()
                }
            )
        except Exception as e:
            self.status = BlockStatus.FAILED
            self.logger.error(f"Random Forest training failed: {str(e)}")
            return BlockOutput(
                block_id=self.block_id,
                status=BlockStatus.FAILED,
                errors=[str(e)]
            )

    def _create_features(self, data: pd.DataFrame) -> tuple:
        """Create feature matrix for Random Forest training"""
        features_list = []

        # Basic user and item indices
        user_indices = data['user_id'].map(self.user_map).values
        item_indices = data['item_id'].map(self.item_map).values

        features_list.append(user_indices.reshape(-1, 1))
        features_list.append(item_indices.reshape(-1, 1))

        # User statistics
        user_stats = data.groupby('user_id')['rating'].agg(['mean', 'count', 'std']).reset_index()
        user_stats.columns = ['user_id', 'user_avg_rating', 'user_rating_count', 'user_std']
        user_stats['user_std'] = user_stats['user_std'].fillna(0)
        data_with_stats = data.merge(user_stats, on='user_id', how='left')

        features_list.append(data_with_stats['user_avg_rating'].values.reshape(-1, 1))
        features_list.append(data_with_stats['user_rating_count'].values.reshape(-1, 1))
        features_list.append(data_with_stats['user_std'].values.reshape(-1, 1))

        # Item statistics
        item_stats = data.groupby('item_id')['rating'].agg(['mean', 'count', 'std']).reset_index()
        item_stats.columns = ['item_id', 'item_avg_rating', 'item_rating_count', 'item_std']
        item_stats['item_std'] = item_stats['item_std'].fillna(0)
        data_with_stats = data_with_stats.merge(item_stats, on='item_id', how='left')

        features_list.append(data_with_stats['item_avg_rating'].values.reshape(-1, 1))
        features_list.append(data_with_stats['item_rating_count'].values.reshape(-1, 1))
        features_list.append(data_with_stats['item_std'].values.reshape(-1, 1))

        # Global mean
        global_mean = data['rating'].mean()
        features_list.append(np.full((len(data), 1), global_mean))

        X = np.hstack(features_list)
        y = data['rating'].values

        return X, y

    def _generate_predictions_matrix(self) -> np.ndarray:
        """Generate predictions for all user-item pairs"""
        n_users = len(self.user_ids)
        n_items = len(self.item_ids)
        predictions = np.zeros((n_users, n_items))

        # Generate in batches for efficiency
        batch_size = 10000
        all_pairs = [(u_idx, i_idx) for u_idx in range(n_users) for i_idx in range(n_items)]

        for batch_start in range(0, len(all_pairs), batch_size):
            batch_end = min(batch_start + batch_size, len(all_pairs))
            batch = all_pairs[batch_start:batch_end]

            batch_features = self._create_batch_features(batch)
            batch_preds = self.model.predict(batch_features)

            for i, (u_idx, i_idx) in enumerate(batch):
                predictions[u_idx, i_idx] = batch_preds[i]

        return predictions

    def _create_batch_features(self, batch: List[tuple]) -> np.ndarray:
        """Create features for a batch of user-item pairs"""
        features_list = []

        u_indices = np.array([pair[0] for pair in batch])
        i_indices = np.array([pair[1] for pair in batch])

        features_list.append(u_indices.reshape(-1, 1))
        features_list.append(i_indices.reshape(-1, 1))

        # Use zeros for statistics (simplified for prediction)
        features_list.append(np.zeros((len(batch), 1)))  # user_avg_rating
        features_list.append(np.zeros((len(batch), 1)))  # user_rating_count
        features_list.append(np.zeros((len(batch), 1)))  # user_std
        features_list.append(np.zeros((len(batch), 1)))  # item_avg_rating
        features_list.append(np.zeros((len(batch), 1)))  # item_rating_count
        features_list.append(np.zeros((len(batch), 1)))  # item_std
        features_list.append(np.full((len(batch), 1), 3.5))  # global_mean

        return np.hstack(features_list)

    def get_schema(self) -> Dict[str, Any]:
        return {
            'type': 'random-forest',
            'inputs': {
                'split-data': {'type': 'dict', 'required': False},
                'processed-data': {'type': 'DataFrame', 'required': False}
            },
            'outputs': {'model': {'type': 'dict'}},
            'config': {
                'n_estimators': {'type': 'int', 'default': 100},
                'max_depth': {'type': 'int', 'default': None},
                'min_samples_split': {'type': 'int', 'default': 2},
                'min_samples_leaf': {'type': 'int', 'default': 1},
                'max_features': {'type': 'str', 'default': 'sqrt'},
                'random_state': {'type': 'int', 'default': 42}
            }
        }
