"""
Evaluation Metrics for Recommender Systems
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from sklearn.metrics import mean_squared_error, mean_absolute_error


class RecommenderMetrics:
    """
    Collection of evaluation metrics for recommendation systems

    Supports both rating prediction metrics (RMSE, MAE) and
    ranking metrics (Precision@K, Recall@K, NDCG@K, MAP@K)
    """

    @staticmethod
    def calculate_rating_metric(
        y_true: np.ndarray,
        y_pred: np.ndarray,
        metric: str
    ) -> float:
        """
        Calculate rating prediction metrics

        Parameters:
        -----------
        y_true : array of true ratings
        y_pred : array of predicted ratings
        metric : str, one of ['rmse', 'mae']

        Returns:
        --------
        score : float
        """
        if metric == 'rmse':
            return np.sqrt(mean_squared_error(y_true, y_pred))
        elif metric == 'mae':
            return mean_absolute_error(y_true, y_pred)
        else:
            raise ValueError(f"Unknown rating metric: {metric}")

    @staticmethod
    def precision_at_k(
        y_true: List[int],
        y_pred: List[int],
        k: int
    ) -> float:
        """
        Calculate Precision@K

        Parameters:
        -----------
        y_true : list of relevant item IDs
        y_pred : list of recommended item IDs (ranked)
        k : int, cutoff for evaluation

        Returns:
        --------
        precision : float in [0, 1]
        """
        if k == 0:
            return 0.0

        # Get top-k predictions
        top_k = y_pred[:k]

        # Count how many are relevant
        relevant_count = len(set(top_k) & set(y_true))

        return relevant_count / k

    @staticmethod
    def recall_at_k(
        y_true: List[int],
        y_pred: List[int],
        k: int
    ) -> float:
        """
        Calculate Recall@K

        Parameters:
        -----------
        y_true : list of relevant item IDs
        y_pred : list of recommended item IDs (ranked)
        k : int, cutoff for evaluation

        Returns:
        --------
        recall : float in [0, 1]
        """
        if len(y_true) == 0:
            return 0.0

        # Get top-k predictions
        top_k = y_pred[:k]

        # Count how many relevant items were retrieved
        relevant_count = len(set(top_k) & set(y_true))

        return relevant_count / len(y_true)

    @staticmethod
    def dcg_at_k(
        y_true: List[int],
        y_pred: List[int],
        k: int
    ) -> float:
        """
        Calculate Discounted Cumulative Gain at K

        Parameters:
        -----------
        y_true : list of relevant item IDs
        y_pred : list of recommended item IDs (ranked)
        k : int, cutoff for evaluation

        Returns:
        --------
        dcg : float
        """
        top_k = y_pred[:k]

        dcg = 0.0
        for i, item in enumerate(top_k, 1):
            if item in y_true:
                dcg += 1.0 / np.log2(i + 1)

        return dcg

    @staticmethod
    def ndcg_at_k(
        y_true: List[int],
        y_pred: List[int],
        k: int
    ) -> float:
        """
        Calculate Normalized Discounted Cumulative Gain at K

        Parameters:
        -----------
        y_true : list of relevant item IDs
        y_pred : list of recommended item IDs (ranked)
        k : int, cutoff for evaluation

        Returns:
        --------
        ndcg : float in [0, 1]
        """
        dcg = RecommenderMetrics.dcg_at_k(y_true, y_pred, k)

        # Calculate ideal DCG (best possible ranking)
        ideal_pred = y_true[:k]
        idcg = RecommenderMetrics.dcg_at_k(y_true, ideal_pred, k)

        if idcg == 0:
            return 0.0

        return dcg / idcg

    @staticmethod
    def map_at_k(
        y_true: List[int],
        y_pred: List[int],
        k: int
    ) -> float:
        """
        Calculate Mean Average Precision at K

        Parameters:
        -----------
        y_true : list of relevant item IDs
        y_pred : list of recommended item IDs (ranked)
        k : int, cutoff for evaluation

        Returns:
        --------
        map : float in [0, 1]
        """
        if len(y_true) == 0:
            return 0.0

        top_k = y_pred[:k]
        relevant_set = set(y_true)

        score = 0.0
        num_hits = 0.0

        for i, item in enumerate(top_k, 1):
            if item in relevant_set:
                num_hits += 1.0
                score += num_hits / i

        return score / min(len(y_true), k)

    @staticmethod
    def hit_rate_at_k(
        y_true: List[int],
        y_pred: List[int],
        k: int
    ) -> float:
        """
        Calculate Hit Rate at K (binary: 1 if any relevant item in top-k, 0 otherwise)

        Parameters:
        -----------
        y_true : list of relevant item IDs
        y_pred : list of recommended item IDs (ranked)
        k : int, cutoff for evaluation

        Returns:
        --------
        hit_rate : float (0 or 1)
        """
        top_k = set(y_pred[:k])
        relevant_set = set(y_true)

        return 1.0 if len(top_k & relevant_set) > 0 else 0.0

    def calculate_ranking_metric(
        self,
        test_data: pd.DataFrame,
        model,
        metric: str,
        k: int
    ) -> float:
        """
        Calculate ranking metrics for a model on test data

        Parameters:
        -----------
        test_data : DataFrame with columns [user_id, item_id, rating]
        model : trained recommender model with predict() method
        metric : str, one of ['precision', 'recall', 'ndcg', 'map', 'hit_rate']
        k : int, cutoff for evaluation

        Returns:
        --------
        average_score : float, average metric across all users
        """
        # Group test data by user
        user_groups = test_data.groupby('user_id')

        scores = []

        for user_id, group in user_groups:
            # Get ground truth relevant items for this user
            relevant_items = group['item_id'].tolist()

            # Get model recommendations
            try:
                recommendations = model.predict([user_id], top_k=k)
                predicted_items = [item_id for item_id, _ in recommendations[user_id]]
            except:
                continue

            # Calculate metric
            if metric == 'precision':
                score = self.precision_at_k(relevant_items, predicted_items, k)
            elif metric == 'recall':
                score = self.recall_at_k(relevant_items, predicted_items, k)
            elif metric == 'ndcg':
                score = self.ndcg_at_k(relevant_items, predicted_items, k)
            elif metric == 'map':
                score = self.map_at_k(relevant_items, predicted_items, k)
            elif metric == 'hit_rate':
                score = self.hit_rate_at_k(relevant_items, predicted_items, k)
            else:
                raise ValueError(f"Unknown ranking metric: {metric}")

            scores.append(score)

        return np.mean(scores) if scores else 0.0


# Test the metrics
if __name__ == '__main__':
    print("Testing RecommenderMetrics")
    print("=" * 50)

    metrics = RecommenderMetrics()

    # Test 1: Rating metrics
    print("\nTest 1: Rating Metrics")
    print("-" * 50)

    y_true = np.array([4.0, 3.5, 5.0, 2.0, 4.5])
    y_pred = np.array([3.8, 3.7, 4.8, 2.5, 4.2])

    rmse = metrics.calculate_rating_metric(y_true, y_pred, 'rmse')
    mae = metrics.calculate_rating_metric(y_true, y_pred, 'mae')

    print(f"RMSE: {rmse:.4f}")
    print(f"MAE: {mae:.4f}")

    # Test 2: Precision and Recall
    print("\n\nTest 2: Precision and Recall @K")
    print("-" * 50)

    relevant_items = [1, 3, 5, 7, 9]
    recommended_items = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    for k in [5, 10]:
        precision = metrics.precision_at_k(relevant_items, recommended_items, k)
        recall = metrics.recall_at_k(relevant_items, recommended_items, k)
        print(f"K={k}: Precision={precision:.4f}, Recall={recall:.4f}")

    # Test 3: NDCG
    print("\n\nTest 3: NDCG @K")
    print("-" * 50)

    relevant_items = [1, 3, 5, 7, 9]
    recommended_items = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    for k in [5, 10]:
        ndcg = metrics.ndcg_at_k(relevant_items, recommended_items, k)
        print(f"NDCG@{k}: {ndcg:.4f}")

    # Test 4: MAP
    print("\n\nTest 4: MAP @K")
    print("-" * 50)

    relevant_items = [1, 3, 5, 7, 9]
    recommended_items = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    for k in [5, 10]:
        map_score = metrics.map_at_k(relevant_items, recommended_items, k)
        print(f"MAP@{k}: {map_score:.4f}")

    # Test 5: Hit Rate
    print("\n\nTest 5: Hit Rate @K")
    print("-" * 50)

    test_cases = [
        ([1, 3, 5], [1, 2, 4, 6, 7]),  # Hit
        ([1, 3, 5], [2, 4, 6, 8, 10]),  # Miss
    ]

    for i, (relevant, recommended) in enumerate(test_cases, 1):
        hit_rate = metrics.hit_rate_at_k(relevant, recommended, 5)
        print(f"Test case {i}: Hit Rate@5 = {hit_rate:.0f}")
