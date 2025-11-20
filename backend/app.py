"""
Mammoth Recommender System Backend API

This Flask application provides endpoints for executing recommendation algorithms
including XGBoost, Random Forests, and traditional collaborative filtering methods.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import pandas as pd
from typing import Dict, Any, List
import logging

# Import model implementations
from models.xgboost_recommender import XGBoostRecommender
from models.random_forest_recommender import RandomForestRecommender
from models.matrix_factorization import MatrixFactorization
from models.collaborative_filtering import CollaborativeFiltering
from utils.data_loader import DataLoader
from utils.metrics import RecommenderMetrics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Store active models and data
active_pipelines = {}


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'mammoth-backend'}), 200


@app.route('/api/data/load', methods=['POST'])
def load_data():
    """
    Load and prepare dataset

    Request body:
    {
        "source": "movielens-100k | synthetic",
        "sample_size": 1000,
        "train_test_split": 0.8
    }
    """
    try:
        data = request.json
        source = data.get('source', 'synthetic')
        sample_size = data.get('sample_size', 1000)
        split_ratio = data.get('train_test_split', 0.8)

        loader = DataLoader()

        if source == 'movielens-100k':
            dataset = loader.load_movielens_100k()
        else:
            dataset = loader.generate_synthetic(
                n_users=100,
                n_items=200,
                n_interactions=sample_size
            )

        train, test = loader.train_test_split(dataset, split_ratio)

        # Store dataset
        pipeline_id = f"pipeline_{len(active_pipelines) + 1}"
        active_pipelines[pipeline_id] = {
            'train': train,
            'test': test,
            'metadata': {
                'n_users': dataset['user_id'].nunique(),
                'n_items': dataset['item_id'].nunique(),
                'n_interactions': len(dataset),
                'sparsity': 1 - (len(dataset) / (dataset['user_id'].nunique() * dataset['item_id'].nunique()))
            }
        }

        return jsonify({
            'success': True,
            'pipeline_id': pipeline_id,
            'metadata': active_pipelines[pipeline_id]['metadata'],
            'train_size': len(train),
            'test_size': len(test)
        }), 200

    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/models/train', methods=['POST'])
def train_model():
    """
    Train a recommendation model

    Request body:
    {
        "pipeline_id": "pipeline_1",
        "model_type": "xgboost | random_forest | matrix_factorization | collaborative_filtering",
        "config": {
            ... model-specific configuration ...
        }
    }
    """
    try:
        data = request.json
        pipeline_id = data.get('pipeline_id')
        model_type = data.get('model_type')
        config = data.get('config', {})

        if pipeline_id not in active_pipelines:
            return jsonify({'success': False, 'error': 'Invalid pipeline_id'}), 400

        train_data = active_pipelines[pipeline_id]['train']

        # Initialize and train model
        if model_type == 'xgboost':
            model = XGBoostRecommender(**config)
        elif model_type == 'random_forest':
            model = RandomForestRecommender(**config)
        elif model_type == 'matrix_factorization':
            model = MatrixFactorization(**config)
        elif model_type == 'collaborative_filtering':
            model = CollaborativeFiltering(**config)
        else:
            return jsonify({'success': False, 'error': f'Unknown model type: {model_type}'}), 400

        # Train the model
        training_history = model.fit(train_data)

        # Store trained model
        active_pipelines[pipeline_id]['model'] = model
        active_pipelines[pipeline_id]['model_type'] = model_type
        active_pipelines[pipeline_id]['training_history'] = training_history

        return jsonify({
            'success': True,
            'pipeline_id': pipeline_id,
            'model_type': model_type,
            'training_history': training_history
        }), 200

    except Exception as e:
        logger.error(f"Error training model: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/models/predict', methods=['POST'])
def predict():
    """
    Generate predictions using trained model

    Request body:
    {
        "pipeline_id": "pipeline_1",
        "user_ids": [1, 2, 3],
        "top_k": 10
    }
    """
    try:
        data = request.json
        pipeline_id = data.get('pipeline_id')
        user_ids = data.get('user_ids')
        top_k = data.get('top_k', 10)

        if pipeline_id not in active_pipelines:
            return jsonify({'success': False, 'error': 'Invalid pipeline_id'}), 400

        if 'model' not in active_pipelines[pipeline_id]:
            return jsonify({'success': False, 'error': 'No trained model found'}), 400

        model = active_pipelines[pipeline_id]['model']

        # Generate predictions
        predictions = model.predict(user_ids, top_k=top_k)

        return jsonify({
            'success': True,
            'predictions': predictions
        }), 200

    except Exception as e:
        logger.error(f"Error generating predictions: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/models/evaluate', methods=['POST'])
def evaluate_model():
    """
    Evaluate trained model on test data

    Request body:
    {
        "pipeline_id": "pipeline_1",
        "metrics": ["rmse", "precision", "recall", "ndcg"],
        "k_values": [5, 10, 20]
    }
    """
    try:
        data = request.json
        pipeline_id = data.get('pipeline_id')
        metric_names = data.get('metrics', ['rmse', 'mae', 'precision', 'recall', 'ndcg'])
        k_values = data.get('k_values', [5, 10, 20])

        if pipeline_id not in active_pipelines:
            return jsonify({'success': False, 'error': 'Invalid pipeline_id'}), 400

        if 'model' not in active_pipelines[pipeline_id]:
            return jsonify({'success': False, 'error': 'No trained model found'}), 400

        model = active_pipelines[pipeline_id]['model']
        test_data = active_pipelines[pipeline_id]['test']

        # Generate predictions on test set
        test_predictions = model.predict_ratings(test_data)

        # Calculate metrics
        metrics_calc = RecommenderMetrics()
        results = {}

        for metric_name in metric_names:
            if metric_name in ['rmse', 'mae']:
                results[metric_name] = metrics_calc.calculate_rating_metric(
                    test_data['rating'].values,
                    test_predictions,
                    metric_name
                )
            elif metric_name in ['precision', 'recall', 'ndcg', 'map']:
                for k in k_values:
                    results[f'{metric_name}@{k}'] = metrics_calc.calculate_ranking_metric(
                        test_data,
                        model,
                        metric_name,
                        k
                    )

        # Store evaluation results
        active_pipelines[pipeline_id]['evaluation'] = results

        return jsonify({
            'success': True,
            'metrics': results
        }), 200

    except Exception as e:
        logger.error(f"Error evaluating model: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/models/compare', methods=['POST'])
def compare_models():
    """
    Compare multiple models on the same dataset

    Request body:
    {
        "pipeline_id": "pipeline_1",
        "model_configs": [
            {"type": "xgboost", "config": {...}},
            {"type": "random_forest", "config": {...}},
            {"type": "matrix_factorization", "config": {...}}
        ],
        "metrics": ["rmse", "precision@10", "ndcg@10"]
    }
    """
    try:
        data = request.json
        pipeline_id = data.get('pipeline_id')
        model_configs = data.get('model_configs', [])
        metrics_to_compute = data.get('metrics', ['rmse', 'precision@10'])

        if pipeline_id not in active_pipelines:
            return jsonify({'success': False, 'error': 'Invalid pipeline_id'}), 400

        train_data = active_pipelines[pipeline_id]['train']
        test_data = active_pipelines[pipeline_id]['test']

        comparison_results = []

        for model_config in model_configs:
            model_type = model_config['type']
            config = model_config.get('config', {})

            # Train model
            if model_type == 'xgboost':
                model = XGBoostRecommender(**config)
            elif model_type == 'random_forest':
                model = RandomForestRecommender(**config)
            elif model_type == 'matrix_factorization':
                model = MatrixFactorization(**config)
            elif model_type == 'collaborative_filtering':
                model = CollaborativeFiltering(**config)
            else:
                continue

            model.fit(train_data)

            # Evaluate
            metrics_calc = RecommenderMetrics()
            model_metrics = {}

            test_predictions = model.predict_ratings(test_data)

            for metric_name in metrics_to_compute:
                if '@' in metric_name:
                    metric, k = metric_name.split('@')
                    model_metrics[metric_name] = metrics_calc.calculate_ranking_metric(
                        test_data,
                        model,
                        metric,
                        int(k)
                    )
                else:
                    model_metrics[metric_name] = metrics_calc.calculate_rating_metric(
                        test_data['rating'].values,
                        test_predictions,
                        metric_name
                    )

            comparison_results.append({
                'model_type': model_type,
                'config': config,
                'metrics': model_metrics
            })

        return jsonify({
            'success': True,
            'comparison': comparison_results
        }), 200

    except Exception as e:
        logger.error(f"Error comparing models: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/pipeline/info/<pipeline_id>', methods=['GET'])
def get_pipeline_info(pipeline_id):
    """Get information about a pipeline"""
    if pipeline_id not in active_pipelines:
        return jsonify({'success': False, 'error': 'Invalid pipeline_id'}), 404

    pipeline = active_pipelines[pipeline_id]

    info = {
        'pipeline_id': pipeline_id,
        'metadata': pipeline.get('metadata', {}),
        'has_model': 'model' in pipeline,
        'model_type': pipeline.get('model_type'),
        'has_evaluation': 'evaluation' in pipeline,
        'evaluation': pipeline.get('evaluation', {})
    }

    return jsonify({'success': True, 'info': info}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
