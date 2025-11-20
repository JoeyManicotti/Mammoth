"""XGBoost Block - Gradient Boosting for Recommendations"""

import numpy as np
import pandas as pd
from typing import Any, Dict, List
from .base import BaseBlock, BlockOutput, BlockStatus

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False


class XGBoostBlock(BaseBlock):
    """Gradient boosting decision trees for recommendations

    Uses XGBoost regression to predict user-item ratings.
    Features are created from user/item IDs and optional additional features.
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
        if not XGBOOST_AVAILABLE:
            errors.append("XGBoost library not installed. Install with: pip install xgboost")

        n_estimators = self.config.get('n_estimators', 100)
        if n_estimators < 1:
            errors.append("n_estimators must be >= 1")

        max_depth = self.config.get('max_depth', 6)
        if max_depth < 1:
            errors.append("max_depth must be >= 1")

        return errors

    def execute(self, inputs: Dict[str, Any]) -> BlockOutput:
        self.status = BlockStatus.RUNNING
        try:
            if not XGBOOST_AVAILABLE:
                raise ImportError("XGBoost library not installed")

            # Get training data
            split_data = inputs.get('split-data', {})
            if split_data and 'train' in split_data:
                train_data = split_data['train']
            else:
                train_data = inputs.get('processed-data')

            if train_data is None:
                raise ValueError("Missing training data")

            # Get optional features (user/item metadata)
            user_features = inputs.get('user-features')
            item_features = inputs.get('item-features')

            # Create user and item mappings
            self.user_ids = sorted(train_data['user_id'].unique())
            self.item_ids = sorted(train_data['item_id'].unique())
            self.user_map = {uid: idx for idx, uid in enumerate(self.user_ids)}
            self.item_map = {iid: idx for idx, iid in enumerate(self.item_ids)}

            # Build feature matrix
            X_train, y_train = self._create_features(
                train_data, user_features, item_features
            )

            # Configure XGBoost
            params = {
                'n_estimators': self.config.get('n_estimators', 100),
                'max_depth': self.config.get('max_depth', 6),
                'learning_rate': self.config.get('learning_rate', 0.1),
                'subsample': self.config.get('subsample', 0.8),
                'colsample_bytree': self.config.get('colsample_bytree', 0.8),
                'objective': 'reg:squarederror',
                'random_state': self.config.get('random_state', 42),
                'n_jobs': -1
            }

            # Train model
            self.model = xgb.XGBRegressor(**params)
            self.model.fit(X_train, y_train, verbose=False)

            # Generate predictions matrix
            predictions = self._generate_predictions_matrix(user_features, item_features)

            # Get feature importance
            feature_importance = self.model.feature_importances_
            top_features = np.argsort(feature_importance)[-5:][::-1]

            model_data = {
                'type': 'xgboost',
                'xgb_model': self.model,
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
                    'max_depth': params['max_depth'],
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
            self.logger.error(f"XGBoost training failed: {str(e)}")
            return BlockOutput(
                block_id=self.block_id,
                status=BlockStatus.FAILED,
                errors=[str(e)]
            )

    def _create_features(
        self,
        data: pd.DataFrame,
        user_features: pd.DataFrame = None,
        item_features: pd.DataFrame = None
    ) -> tuple:
        """Create feature matrix for XGBoost training

        Features include:
        - User ID (mapped to index)
        - Item ID (mapped to index)
        - User statistics (avg rating, rating count)
        - Item statistics (avg rating, rating count)
        - Optional: additional user/item features
        """
        features_list = []

        # Basic user and item indices
        user_indices = data['user_id'].map(self.user_map).values
        item_indices = data['item_id'].map(self.item_map).values

        features_list.append(user_indices.reshape(-1, 1))
        features_list.append(item_indices.reshape(-1, 1))

        # User statistics
        user_stats = data.groupby('user_id')['rating'].agg(['mean', 'count']).reset_index()
        user_stats.columns = ['user_id', 'user_avg_rating', 'user_rating_count']
        data_with_stats = data.merge(user_stats, on='user_id', how='left')

        features_list.append(data_with_stats['user_avg_rating'].values.reshape(-1, 1))
        features_list.append(data_with_stats['user_rating_count'].values.reshape(-1, 1))

        # Item statistics
        item_stats = data.groupby('item_id')['rating'].agg(['mean', 'count']).reset_index()
        item_stats.columns = ['item_id', 'item_avg_rating', 'item_rating_count']
        data_with_stats = data_with_stats.merge(item_stats, on='item_id', how='left')

        features_list.append(data_with_stats['item_avg_rating'].values.reshape(-1, 1))
        features_list.append(data_with_stats['item_rating_count'].values.reshape(-1, 1))

        # Global mean rating
        global_mean = data['rating'].mean()
        features_list.append(np.full((len(data), 1), global_mean))

        # Optional: Add user/item metadata features
        if user_features is not None:
            user_feat_cols = [c for c in user_features.columns if c != 'user_id']
            if user_feat_cols:
                data_with_stats = data_with_stats.merge(
                    user_features[['user_id'] + user_feat_cols],
                    on='user_id',
                    how='left'
                )
                for col in user_feat_cols:
                    features_list.append(data_with_stats[col].fillna(0).values.reshape(-1, 1))

        if item_features is not None:
            item_feat_cols = [c for c in item_features.columns if c != 'item_id']
            if item_feat_cols:
                data_with_stats = data_with_stats.merge(
                    item_features[['item_id'] + item_feat_cols],
                    on='item_id',
                    how='left'
                )
                for col in item_feat_cols:
                    features_list.append(data_with_stats[col].fillna(0).values.reshape(-1, 1))

        X = np.hstack(features_list)
        y = data['rating'].values

        return X, y

    def _generate_predictions_matrix(
        self,
        user_features: pd.DataFrame = None,
        item_features: pd.DataFrame = None
    ) -> np.ndarray:
        """Generate predictions for all user-item pairs"""
        n_users = len(self.user_ids)
        n_items = len(self.item_ids)
        predictions = np.zeros((n_users, n_items))

        # Create a synthetic dataset with all user-item combinations
        # For efficiency, we'll do this in batches
        batch_size = 10000

        all_pairs = []
        for u_idx, user_id in enumerate(self.user_ids):
            for i_idx, item_id in enumerate(self.item_ids):
                all_pairs.append((u_idx, i_idx, user_id, item_id))

        for batch_start in range(0, len(all_pairs), batch_size):
            batch_end = min(batch_start + batch_size, len(all_pairs))
            batch = all_pairs[batch_start:batch_end]

            batch_features = self._create_batch_features(
                batch, user_features, item_features
            )

            batch_preds = self.model.predict(batch_features)

            for i, (u_idx, i_idx, _, _) in enumerate(batch):
                predictions[u_idx, i_idx] = batch_preds[i]

        return predictions

    def _create_batch_features(
        self,
        batch: List[tuple],
        user_features: pd.DataFrame = None,
        item_features: pd.DataFrame = None
    ) -> np.ndarray:
        """Create features for a batch of user-item pairs"""
        features_list = []

        u_indices = np.array([pair[0] for pair in batch])
        i_indices = np.array([pair[1] for pair in batch])

        features_list.append(u_indices.reshape(-1, 1))
        features_list.append(i_indices.reshape(-1, 1))

        # For prediction, we'll use global statistics or zeros
        # This is a simplification - in practice, you'd compute these from training data
        features_list.append(np.zeros((len(batch), 1)))  # user_avg_rating placeholder
        features_list.append(np.zeros((len(batch), 1)))  # user_rating_count placeholder
        features_list.append(np.zeros((len(batch), 1)))  # item_avg_rating placeholder
        features_list.append(np.zeros((len(batch), 1)))  # item_rating_count placeholder
        features_list.append(np.full((len(batch), 1), 3.5))  # global_mean placeholder

        # Add user/item features if available
        if user_features is not None:
            user_feat_cols = [c for c in user_features.columns if c != 'user_id']
            for col in user_feat_cols:
                features_list.append(np.zeros((len(batch), 1)))

        if item_features is not None:
            item_feat_cols = [c for c in item_features.columns if c != 'item_id']
            for col in item_feat_cols:
                features_list.append(np.zeros((len(batch), 1)))

        return np.hstack(features_list)

    def get_schema(self) -> Dict[str, Any]:
        return {
            'type': 'xgboost',
            'inputs': {
                'split-data': {'type': 'dict', 'required': False},
                'processed-data': {'type': 'DataFrame', 'required': False},
                'user-features': {'type': 'DataFrame', 'required': False},
                'item-features': {'type': 'DataFrame', 'required': False}
            },
            'outputs': {'model': {'type': 'dict'}},
            'config': {
                'n_estimators': {'type': 'int', 'default': 100},
                'max_depth': {'type': 'int', 'default': 6},
                'learning_rate': {'type': 'float', 'default': 0.1},
                'subsample': {'type': 'float', 'default': 0.8},
                'colsample_bytree': {'type': 'float', 'default': 0.8},
                'random_state': {'type': 'int', 'default': 42}
            }
        }
