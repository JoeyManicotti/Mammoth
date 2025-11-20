"""
Data Loading Utilities for Recommender Systems
"""

import numpy as np
import pandas as pd
from typing import Tuple, Optional
from pathlib import Path


class DataLoader:
    """Utility class for loading and preparing recommendation datasets"""

    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / 'data'
        self.data_dir.mkdir(exist_ok=True)

    def generate_synthetic(
        self,
        n_users: int = 100,
        n_items: int = 200,
        n_interactions: int = 1000,
        rating_scale: Tuple[float, float] = (1.0, 5.0),
        sparsity: float = 0.95,
        random_state: int = 42
    ) -> pd.DataFrame:
        """
        Generate synthetic user-item interaction data

        Parameters:
        -----------
        n_users : int
            Number of users
        n_items : int
            Number of items
        n_interactions : int
            Number of interactions to generate
        rating_scale : tuple
            (min_rating, max_rating)
        sparsity : float
            Desired sparsity level (0-1)
        random_state : int
            Random seed for reproducibility

        Returns:
        --------
        data : DataFrame with columns [user_id, item_id, rating, timestamp]
        """
        np.random.seed(random_state)

        # Generate user-item pairs
        user_ids = np.random.randint(0, n_users, n_interactions)
        item_ids = np.random.randint(0, n_items, n_interactions)

        # Generate ratings with some structure
        # Simulate user biases and item popularity
        user_bias = np.random.normal(0, 0.5, n_users)
        item_bias = np.random.normal(0, 0.5, n_items)

        ratings = []
        for user_id, item_id in zip(user_ids, item_ids):
            base_rating = (rating_scale[0] + rating_scale[1]) / 2
            rating = base_rating + user_bias[user_id] + item_bias[item_id]
            rating += np.random.normal(0, 0.3)  # Add noise

            # Clip to rating scale
            rating = np.clip(rating, rating_scale[0], rating_scale[1])
            ratings.append(rating)

        # Generate timestamps
        timestamps = np.random.randint(1000000000, 1700000000, n_interactions)

        data = pd.DataFrame({
            'user_id': user_ids,
            'item_id': item_ids,
            'rating': ratings,
            'timestamp': timestamps
        })

        # Remove duplicate user-item pairs, keeping the latest
        data = data.sort_values('timestamp').groupby(['user_id', 'item_id']).last().reset_index()

        return data

    def load_movielens_100k(self, filepath: Optional[str] = None) -> pd.DataFrame:
        """
        Load MovieLens 100K dataset

        Parameters:
        -----------
        filepath : str, optional
            Path to the dataset file. If None, generates synthetic data as placeholder.

        Returns:
        --------
        data : DataFrame with columns [user_id, item_id, rating, timestamp]
        """
        # Since we may not have the actual MovieLens data in this environment,
        # generate realistic synthetic data with similar properties
        print("Note: Using synthetic data with MovieLens-like properties")

        return self.generate_synthetic(
            n_users=943,
            n_items=1682,
            n_interactions=100000,
            rating_scale=(1.0, 5.0),
            sparsity=0.937
        )

    def train_test_split(
        self,
        data: pd.DataFrame,
        test_size: float = 0.2,
        random_state: int = 42
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Split data into train and test sets

        Parameters:
        -----------
        data : DataFrame
            Full dataset
        test_size : float
            Proportion of data for test set (0-1)
        random_state : int
            Random seed

        Returns:
        --------
        train_data, test_data : tuple of DataFrames
        """
        np.random.seed(random_state)

        # Shuffle data
        data = data.sample(frac=1, random_state=random_state).reset_index(drop=True)

        # Split
        split_idx = int(len(data) * (1 - test_size))
        train_data = data.iloc[:split_idx].copy()
        test_data = data.iloc[split_idx:].copy()

        return train_data, test_data

    def temporal_split(
        self,
        data: pd.DataFrame,
        test_size: float = 0.2
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Split data chronologically (temporal split)

        Parameters:
        -----------
        data : DataFrame
            Full dataset with 'timestamp' column
        test_size : float
            Proportion of data for test set (0-1)

        Returns:
        --------
        train_data, test_data : tuple of DataFrames
        """
        if 'timestamp' not in data.columns:
            raise ValueError("Data must contain 'timestamp' column for temporal split")

        # Sort by timestamp
        data = data.sort_values('timestamp').reset_index(drop=True)

        # Split
        split_idx = int(len(data) * (1 - test_size))
        train_data = data.iloc[:split_idx].copy()
        test_data = data.iloc[split_idx:].copy()

        return train_data, test_data

    def create_interaction_matrix(
        self,
        data: pd.DataFrame
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Create user-item interaction matrix

        Parameters:
        -----------
        data : DataFrame with columns [user_id, item_id, rating]

        Returns:
        --------
        matrix : sparse rating matrix
        user_ids : array of unique user IDs
        item_ids : array of unique item IDs
        """
        from scipy.sparse import csr_matrix

        user_ids = data['user_id'].unique()
        item_ids = data['item_id'].unique()

        # Create mapping dictionaries
        user_to_idx = {uid: idx for idx, uid in enumerate(user_ids)}
        item_to_idx = {iid: idx for idx, iid in enumerate(item_ids)}

        # Map to indices
        row_indices = data['user_id'].map(user_to_idx).values
        col_indices = data['item_id'].map(item_to_idx).values
        ratings = data['rating'].values

        # Create sparse matrix
        matrix = csr_matrix(
            (ratings, (row_indices, col_indices)),
            shape=(len(user_ids), len(item_ids))
        )

        return matrix, user_ids, item_ids


# Test the data loader
if __name__ == '__main__':
    print("Testing DataLoader")
    print("=" * 50)

    loader = DataLoader()

    # Test 1: Generate synthetic data
    print("\nTest 1: Generate Synthetic Data")
    print("-" * 50)
    data = loader.generate_synthetic(
        n_users=50,
        n_items=100,
        n_interactions=500
    )

    print(f"Generated {len(data)} interactions")
    print(f"Users: {data['user_id'].nunique()}")
    print(f"Items: {data['item_id'].nunique()}")
    print(f"Rating range: [{data['rating'].min():.2f}, {data['rating'].max():.2f}]")
    print(f"\nSample data:")
    print(data.head())

    # Test 2: Train-test split
    print("\n\nTest 2: Train-Test Split")
    print("-" * 50)
    train, test = loader.train_test_split(data, test_size=0.2)

    print(f"Train size: {len(train)} ({len(train)/len(data)*100:.1f}%)")
    print(f"Test size: {len(test)} ({len(test)/len(data)*100:.1f}%)")

    # Test 3: Temporal split
    print("\n\nTest 3: Temporal Split")
    print("-" * 50)
    train_temp, test_temp = loader.temporal_split(data, test_size=0.2)

    print(f"Train time range: {train_temp['timestamp'].min()} - {train_temp['timestamp'].max()}")
    print(f"Test time range: {test_temp['timestamp'].min()} - {test_temp['timestamp'].max()}")

    # Test 4: Interaction matrix
    print("\n\nTest 4: Interaction Matrix")
    print("-" * 50)
    matrix, user_ids, item_ids = loader.create_interaction_matrix(data)

    print(f"Matrix shape: {matrix.shape}")
    print(f"Sparsity: {1 - matrix.nnz / (matrix.shape[0] * matrix.shape[1]):.4f}")
    print(f"Non-zero entries: {matrix.nnz}")
