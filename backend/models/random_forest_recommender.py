"""
Random Forest-based Recommender System

This module implements a recommendation algorithm using Random Forest regression.
Ensemble of decision trees for robust predictions.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder


class RandomForestRecommender:
    """
    Random Forest Recommender System

    Uses an ensemble of decision trees to predict user-item ratings.
    Robust to overfitting and handles non-linear relationships well.

    Parameters:
    -----------
    n_estimators : int, default=100
        Number of trees in the forest
    max_depth : int, default=None
        Maximum depth of trees (None = unlimited)
    min_samples_split : int, default=2
        Minimum samples required to split an internal node
    min_samples_leaf : int, default=1
        Minimum samples required to be at a leaf node
    max_features : str or int, default='sqrt'
        Number of features to consider when looking for best split
    n_jobs : int, default=-1
        Number of parallel jobs (-1 = use all cores)
    """

    def __init__(
        self,
        n_estimators: int = 100,
        max_depth: Optional[int] = None,
        min_samples_split: int = 2,
        min_samples_leaf: int = 1,
        max_features: str = 'sqrt',
        n_jobs: int = -1,
        random_state: int = 42
    ):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.min_samples_leaf = min_samples_leaf
        self.max_features = max_features
        self.n_jobs = n_jobs
        self.random_state = random_state

        self.model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            max_features=max_features,
            n_jobs=n_jobs,
            random_state=random_state,
            verbose=0
        )

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

    def fit(self, train_data: pd.DataFrame) -> Dict[str, float]:
        """
        Train the Random Forest model

        Parameters:
        -----------
        train_data : DataFrame with columns [user_id, item_id, rating, ...]

        Returns:
        --------
        training_info : dict with training information
        """
        # Prepare training data
        X_train, y_train = self._prepare_features(train_data, fit_encoders=True)

        # Train model
        self.model.fit(X_train, y_train)

        self.is_fitted = True

        # Calculate training score
        train_score = self.model.score(X_train, y_train)

        return {
            'train_r2_score': train_score,
            'n_estimators': self.n_estimators,
            'max_depth': self.max_depth if self.max_depth else 'None',
            'oob_score': self.model.oob_score_ if hasattr(self.model, 'oob_score_') else None
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
        predictions = self.model.predict(X)

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

        feature_names = ['user_id', 'item_id']  # Base features
        importances = self.model.feature_importances_

        return {name: float(imp) for name, imp in zip(feature_names, importances)}

    def get_tree_predictions(
        self,
        data: pd.DataFrame
    ) -> np.ndarray:
        """
        Get predictions from each tree in the forest

        Returns:
        --------
        predictions : array of shape (n_samples, n_estimators)
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted first")

        X, _ = self._prepare_features(data, fit_encoders=False)

        # Get predictions from each tree
        predictions = np.array([tree.predict(X) for tree in self.model.estimators_])

        return predictions.T  # Shape: (n_samples, n_trees)

    def get_prediction_uncertainty(
        self,
        data: pd.DataFrame
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get prediction mean and standard deviation across trees

        Returns:
        --------
        mean : mean prediction
        std : standard deviation of predictions
        """
        tree_predictions = self.get_tree_predictions(data)

        mean = tree_predictions.mean(axis=1)
        std = tree_predictions.std(axis=1)

        return mean, std


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
    model = RandomForestRecommender(
        n_estimators=50,
        max_depth=10,
        random_state=42
    )

    training_info = model.fit(train_data)
    print(f"Training completed.")
    print(f"  R² Score: {training_info['train_r2_score']:.4f}")
    print(f"  N Estimators: {training_info['n_estimators']}")
    print(f"  Max Depth: {training_info['max_depth']}")

    # Generate predictions
    test_users = [0, 1, 2]
    recommendations = model.predict(test_users, top_k=5)

    print("\nTop-5 recommendations:")
    for user_id, items in recommendations.items():
        print(f"User {user_id}:")
        for item_id, score in items:
            print(f"  Item {item_id}: {score:.2f}")

    # Test Case 2: Prediction uncertainty
    print("\n\nTest Case 2: Prediction Uncertainty")
    print("=" * 50)

    test_data = pd.DataFrame({
        'user_id': [0, 0, 1, 1],
        'item_id': [10, 20, 10, 30]
    })

    mean_pred, std_pred = model.get_prediction_uncertainty(test_data)

    print("Predictions with uncertainty:")
    for i, (user, item, mean, std) in enumerate(zip(
        test_data['user_id'],
        test_data['item_id'],
        mean_pred,
        std_pred
    )):
        print(f"  User {user}, Item {item}: {mean:.2f} ± {std:.2f}")

    # Test Case 3: Feature importance
    print("\n\nTest Case 3: Feature Importance")
    print("=" * 50)

    importance = model.get_feature_importance()
    print("Feature importance scores:")
    for feature, score in sorted(importance.items(), key=lambda x: x[1], reverse=True):
        print(f"  {feature}: {score:.4f}")

    # Test Case 4: Compare shallow vs deep trees
    print("\n\nTest Case 4: Shallow vs Deep Trees")
    print("=" * 50)

    model_shallow = RandomForestRecommender(
        n_estimators=50,
        max_depth=3,
        random_state=42
    )

    model_deep = RandomForestRecommender(
        n_estimators=50,
        max_depth=20,
        random_state=42
    )

    info_shallow = model_shallow.fit(train_data)
    info_deep = model_deep.fit(train_data)

    print(f"Shallow trees (depth=3) R² Score: {info_shallow['train_r2_score']:.4f}")
    print(f"Deep trees (depth=20) R² Score: {info_deep['train_r2_score']:.4f}")
