"""
XGBoost-based Recommender System

This module implements a gradient boosting recommendation algorithm using XGBoost.
It treats recommendation as a regression or ranking problem.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
import xgboost as xgb
from sklearn.preprocessing import LabelEncoder


class XGBoostRecommender:
    """
    XGBoost Recommender System

    Uses gradient boosting trees to predict user-item ratings or rankings.
    Can incorporate user and item features for hybrid recommendations.

    Parameters:
    -----------
    n_estimators : int, default=100
        Number of boosting rounds
    max_depth : int, default=6
        Maximum tree depth
    learning_rate : float, default=0.1
        Step size shrinkage used to prevent overfitting
    objective : str, default='reg:squarederror'
        Learning objective ('reg:squarederror', 'rank:pairwise', 'rank:ndcg')
    reg_alpha : float, default=0.0
        L1 regularization term on weights
    reg_lambda : float, default=1.0
        L2 regularization term on weights
    """

    def __init__(
        self,
        n_estimators: int = 100,
        max_depth: int = 6,
        learning_rate: float = 0.1,
        objective: str = 'reg:squarederror',
        reg_alpha: float = 0.0,
        reg_lambda: float = 1.0,
        random_state: int = 42
    ):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.learning_rate = learning_rate
        self.objective = objective
        self.reg_alpha = reg_alpha
        self.reg_lambda = reg_lambda
        self.random_state = random_state

        self.model = None
        self.user_encoder = LabelEncoder()
        self.item_encoder = LabelEncoder()
        self.is_fitted = False

    def _prepare_features(
        self,
        data: pd.DataFrame,
        fit_encoders: bool = False
    ) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """
        Prepare feature matrix from user-item interactions

        Parameters:
        -----------
        data : DataFrame with columns [user_id, item_id, rating]
        fit_encoders : bool, whether to fit label encoders

        Returns:
        --------
        X : feature matrix
        y : target values (if 'rating' column exists)
        """
        if fit_encoders:
            self.user_encoder.fit(data['user_id'])
            self.item_encoder.fit(data['item_id'])

        # Encode user and item IDs
        user_encoded = self.user_encoder.transform(data['user_id'])
        item_encoded = self.item_encoder.transform(data['item_id'])

        # Create feature matrix
        # Basic features: user_id, item_id
        X = np.column_stack([user_encoded, item_encoded])

        # Add additional features if available
        feature_cols = [col for col in data.columns
                       if col not in ['user_id', 'item_id', 'rating', 'timestamp']]

        if feature_cols:
            additional_features = data[feature_cols].values
            X = np.column_stack([X, additional_features])

        # Extract target if available
        y = data['rating'].values if 'rating' in data.columns else None

        return X, y

    def fit(self, train_data: pd.DataFrame) -> Dict[str, List[float]]:
        """
        Train the XGBoost model

        Parameters:
        -----------
        train_data : DataFrame with columns [user_id, item_id, rating, ...]

        Returns:
        --------
        training_history : dict with training metrics
        """
        # Prepare training data
        X_train, y_train = self._prepare_features(train_data, fit_encoders=True)

        # Create DMatrix for XGBoost
        dtrain = xgb.DMatrix(X_train, label=y_train)

        # Set parameters
        params = {
            'objective': self.objective,
            'max_depth': self.max_depth,
            'learning_rate': self.learning_rate,
            'reg_alpha': self.reg_alpha,
            'reg_lambda': self.reg_lambda,
            'random_state': self.random_state,
            'verbosity': 0
        }

        # Train model with evaluation
        evals_result = {}
        self.model = xgb.train(
            params,
            dtrain,
            num_boost_round=self.n_estimators,
            evals=[(dtrain, 'train')],
            evals_result=evals_result,
            verbose_eval=False
        )

        self.is_fitted = True

        return {
            'train_error': evals_result['train'].get('rmse', [])
        }

    def predict_ratings(self, data: pd.DataFrame) -> np.ndarray:
        """
        Predict ratings for user-item pairs

        Parameters:
        -----------
        data : DataFrame with columns [user_id, item_id, ...]

        Returns:
        --------
        predictions : array of predicted ratings
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before making predictions")

        X, _ = self._prepare_features(data, fit_encoders=False)
        dtest = xgb.DMatrix(X)

        predictions = self.model.predict(dtest)

        return predictions

    def predict(
        self,
        user_ids: List[int],
        top_k: int = 10,
        item_pool: Optional[List[int]] = None
    ) -> Dict[int, List[Tuple[int, float]]]:
        """
        Generate top-K recommendations for users

        Parameters:
        -----------
        user_ids : list of user IDs
        top_k : number of items to recommend
        item_pool : optional list of items to consider (if None, use all items)

        Returns:
        --------
        recommendations : dict mapping user_id to list of (item_id, score) tuples
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before making predictions")

        if item_pool is None:
            item_pool = self.item_encoder.classes_.tolist()

        recommendations = {}

        for user_id in user_ids:
            # Create candidate user-item pairs
            candidates = pd.DataFrame({
                'user_id': [user_id] * len(item_pool),
                'item_id': item_pool
            })

            # Predict scores
            scores = self.predict_ratings(candidates)

            # Get top-K items
            top_indices = np.argsort(scores)[::-1][:top_k]
            top_items = [(item_pool[idx], float(scores[idx]))
                        for idx in top_indices]

            recommendations[user_id] = top_items

        return recommendations

    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance scores"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted first")

        importance = self.model.get_score(importance_type='gain')
        return importance

    def save_model(self, filepath: str):
        """Save model to file"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before saving")

        self.model.save_model(filepath)

    def load_model(self, filepath: str):
        """Load model from file"""
        self.model = xgb.Booster()
        self.model.load_model(filepath)
        self.is_fitted = True


# Test cases
if __name__ == '__main__':
    # Test Case 1: Basic training and prediction
    print("Test Case 1: Basic Training and Prediction")
    print("=" * 50)

    # Generate synthetic data
    np.random.seed(42)
    n_users, n_items = 100, 200
    n_interactions = 1000

    train_data = pd.DataFrame({
        'user_id': np.random.randint(0, n_users, n_interactions),
        'item_id': np.random.randint(0, n_items, n_interactions),
        'rating': np.random.uniform(1, 5, n_interactions)
    })

    # Train model
    model = XGBoostRecommender(
        n_estimators=50,
        max_depth=4,
        learning_rate=0.1
    )

    history = model.fit(train_data)
    print(f"Training completed. Final RMSE: {history['train_error'][-1]:.4f}")

    # Generate predictions
    test_users = [0, 1, 2]
    recommendations = model.predict(test_users, top_k=5)

    print("\nTop-5 recommendations:")
    for user_id, items in recommendations.items():
        print(f"User {user_id}: {items}")

    # Test Case 2: With regularization
    print("\n\nTest Case 2: With Regularization")
    print("=" * 50)

    model_reg = XGBoostRecommender(
        n_estimators=50,
        max_depth=4,
        learning_rate=0.1,
        reg_alpha=0.1,
        reg_lambda=1.0
    )

    history_reg = model_reg.fit(train_data)
    print(f"Training with regularization. Final RMSE: {history_reg['train_error'][-1]:.4f}")

    # Test Case 3: Feature importance
    print("\n\nTest Case 3: Feature Importance")
    print("=" * 50)

    importance = model.get_feature_importance()
    print("Feature importance scores:")
    for feature, score in sorted(importance.items(), key=lambda x: x[1], reverse=True):
        print(f"  {feature}: {score:.4f}")
