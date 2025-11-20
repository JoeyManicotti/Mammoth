"""
Demo Data Generator

Utilities for generating realistic demo datasets for testing and examples.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta


class DemoDataGenerator:
    """Generate realistic demo datasets for recommender systems"""

    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        np.random.seed(random_state)

    def generate_movie_ratings(
        self,
        n_users: int = 100,
        n_movies: int = 200,
        n_ratings: int = 1000,
        genres: Optional[List[str]] = None
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Generate realistic movie rating dataset

        Returns:
            ratings_df: User-movie ratings
            movies_df: Movie metadata
            users_df: User demographics
        """
        if genres is None:
            genres = ['Action', 'Comedy', 'Drama', 'Sci-Fi', 'Romance', 'Thriller', 'Horror', 'Documentary']

        # Generate movie metadata
        movies_data = []
        for movie_id in range(n_movies):
            # Each movie has 1-3 genres
            movie_genres = np.random.choice(genres, size=np.random.randint(1, 4), replace=False)
            release_year = np.random.randint(1980, 2024)
            popularity = np.random.lognormal(mean=0, sigma=1)

            movies_data.append({
                'movie_id': movie_id,
                'title': f'Movie_{movie_id}',
                'genres': '|'.join(movie_genres),
                'release_year': release_year,
                'popularity': popularity
            })

        movies_df = pd.DataFrame(movies_data)

        # Generate user demographics
        users_data = []
        for user_id in range(n_users):
            age = np.random.choice([18, 25, 35, 45, 55, 65], p=[0.1, 0.3, 0.3, 0.2, 0.07, 0.03])
            gender = np.random.choice(['M', 'F', 'Other'], p=[0.48, 0.48, 0.04])
            # User preferences - which genres they like
            favorite_genres = np.random.choice(genres, size=np.random.randint(2, 5), replace=False)

            users_data.append({
                'user_id': user_id,
                'age': age,
                'gender': gender,
                'favorite_genres': '|'.join(favorite_genres)
            })

        users_df = pd.DataFrame(users_data)

        # Generate ratings with realistic patterns
        ratings_data = []
        user_movie_pairs = set()

        # Create user and movie biases
        user_biases = np.random.normal(0, 0.5, n_users)
        movie_biases = np.random.normal(0, 0.3, n_movies)

        while len(ratings_data) < n_ratings:
            user_id = np.random.randint(0, n_users)
            movie_id = np.random.randint(0, n_movies)

            # Skip if already rated
            if (user_id, movie_id) in user_movie_pairs:
                continue

            user_movie_pairs.add((user_id, movie_id))

            # Calculate rating based on:
            # 1. User bias (some users rate higher)
            # 2. Movie bias (some movies are better)
            # 3. Genre match (users like certain genres)
            # 4. Random noise

            base_rating = 3.0
            rating = base_rating + user_biases[user_id] + movie_biases[movie_id]

            # Genre boost
            user_genres = set(users_df.loc[user_id, 'favorite_genres'].split('|'))
            movie_genres = set(movies_df.loc[movie_id, 'genres'].split('|'))
            genre_overlap = len(user_genres & movie_genres) / len(user_genres)
            rating += genre_overlap * 1.0

            # Add noise
            rating += np.random.normal(0, 0.3)

            # Clip to 1-5 range
            rating = np.clip(rating, 1.0, 5.0)

            # Generate timestamp (last 2 years)
            days_ago = np.random.randint(0, 730)
            timestamp = int((datetime.now() - timedelta(days=days_ago)).timestamp())

            ratings_data.append({
                'user_id': user_id,
                'item_id': movie_id,
                'rating': round(rating, 1),
                'timestamp': timestamp
            })

        ratings_df = pd.DataFrame(ratings_data)

        return ratings_df, movies_df, users_df

    def generate_ecommerce_data(
        self,
        n_users: int = 200,
        n_products: int = 500,
        n_interactions: int = 2000
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Generate e-commerce purchase/view data

        Returns:
            interactions_df: User-product interactions
            products_df: Product metadata
        """
        categories = ['Electronics', 'Clothing', 'Home & Garden', 'Sports', 'Books', 'Toys']

        # Generate products
        products_data = []
        for product_id in range(n_products):
            category = np.random.choice(categories)
            price = np.random.lognormal(mean=3, sigma=1)
            rating = np.random.beta(8, 2) * 5  # Skewed towards high ratings
            n_reviews = int(np.random.lognormal(mean=3, sigma=2))

            products_data.append({
                'product_id': product_id,
                'name': f'Product_{product_id}',
                'category': category,
                'price': round(price, 2),
                'avg_rating': round(rating, 1),
                'n_reviews': n_reviews
            })

        products_df = pd.DataFrame(products_data)

        # Generate interactions
        interactions_data = []
        interaction_types = ['view', 'cart', 'purchase']

        for _ in range(n_interactions):
            user_id = np.random.randint(0, n_users)
            product_id = np.random.randint(0, n_products)

            # Interaction type probability: view > cart > purchase
            interaction_type = np.random.choice(
                interaction_types,
                p=[0.7, 0.2, 0.1]
            )

            # Implicit rating based on interaction
            rating_map = {'view': 1.0, 'cart': 3.0, 'purchase': 5.0}
            rating = rating_map[interaction_type]

            timestamp = int((datetime.now() - timedelta(days=np.random.randint(0, 365))).timestamp())

            interactions_data.append({
                'user_id': user_id,
                'item_id': product_id,
                'rating': rating,
                'interaction_type': interaction_type,
                'timestamp': timestamp
            })

        interactions_df = pd.DataFrame(interactions_data)

        return interactions_df, products_df

    def generate_music_streaming_data(
        self,
        n_users: int = 150,
        n_songs: int = 300,
        n_plays: int = 3000
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Generate music streaming data

        Returns:
            plays_df: User listening history
            songs_df: Song metadata
        """
        genres = ['Pop', 'Rock', 'Hip-Hop', 'Electronic', 'Classical', 'Jazz', 'Country', 'R&B']
        artists = [f'Artist_{i}' for i in range(50)]

        # Generate songs
        songs_data = []
        for song_id in range(n_songs):
            genre = np.random.choice(genres)
            artist = np.random.choice(artists)
            duration = np.random.randint(120, 360)  # 2-6 minutes
            release_year = np.random.randint(1990, 2024)
            popularity = np.random.lognormal(mean=5, sigma=2)

            songs_data.append({
                'song_id': song_id,
                'title': f'Song_{song_id}',
                'artist': artist,
                'genre': genre,
                'duration': duration,
                'release_year': release_year,
                'popularity': popularity
            })

        songs_df = pd.DataFrame(songs_data)

        # Generate play history
        plays_data = []

        for _ in range(n_plays):
            user_id = np.random.randint(0, n_users)
            song_id = np.random.randint(0, n_songs)

            # Play completion (0-1)
            completion = np.random.beta(3, 1)  # Skewed towards complete plays

            # Implicit rating: higher completion = higher rating
            rating = 1.0 + completion * 4.0

            # Skip if completion < 0.3
            if completion < 0.3:
                rating = 1.0

            timestamp = int((datetime.now() - timedelta(days=np.random.randint(0, 180))).timestamp())

            plays_data.append({
                'user_id': user_id,
                'item_id': song_id,
                'rating': round(rating, 1),
                'completion': round(completion, 2),
                'timestamp': timestamp
            })

        plays_df = pd.DataFrame(plays_data)

        return plays_df, songs_df

    def save_demo_datasets(self, output_dir: str = 'data/demo'):
        """Generate and save all demo datasets"""
        import os
        os.makedirs(output_dir, exist_ok=True)

        # Movies
        print("Generating movie ratings dataset...")
        ratings, movies, users = self.generate_movie_ratings(
            n_users=200,
            n_movies=500,
            n_ratings=5000
        )
        ratings.to_csv(f'{output_dir}/movie_ratings.csv', index=False)
        movies.to_csv(f'{output_dir}/movies.csv', index=False)
        users.to_csv(f'{output_dir}/users.csv', index=False)
        print(f"  ✓ Saved {len(ratings)} movie ratings")

        # E-commerce
        print("Generating e-commerce dataset...")
        interactions, products = self.generate_ecommerce_data(
            n_users=300,
            n_products=800,
            n_interactions=8000
        )
        interactions.to_csv(f'{output_dir}/ecommerce_interactions.csv', index=False)
        products.to_csv(f'{output_dir}/products.csv', index=False)
        print(f"  ✓ Saved {len(interactions)} e-commerce interactions")

        # Music
        print("Generating music streaming dataset...")
        plays, songs = self.generate_music_streaming_data(
            n_users=250,
            n_songs=600,
            n_plays=10000
        )
        plays.to_csv(f'{output_dir}/music_plays.csv', index=False)
        songs.to_csv(f'{output_dir}/songs.csv', index=False)
        print(f"  ✓ Saved {len(plays)} music plays")

        print(f"\nAll datasets saved to {output_dir}/")


if __name__ == '__main__':
    print("=" * 70)
    print("Mammoth Demo Data Generator")
    print("=" * 70)
    print()

    generator = DemoDataGenerator(random_state=42)

    # Generate and save demo datasets
    generator.save_demo_datasets('data/demo')

    print()
    print("Demo datasets ready! Use them in your workflows:")
    print()
    print("  data = DataSourceBlock('data')")
    print("  data.configure(")
    print("      data_source='csv',")
    print("      file_path='data/demo/movie_ratings.csv'")
    print("  )")
