"""
Comprehensive Test Suite for All Blocks

Tests each block individually and as part of pipelines.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from blocks import *
import unittest


class TestDataSourceBlock(unittest.TestCase):
    """Test Data Source Block"""

    def test_synthetic_data_generation(self):
        block = DataSourceBlock('test-data-source')
        block.configure(
            data_source='synthetic',
            n_users=50,
            n_items=100,
            n_interactions=500
        )

        errors = block.validate_config()
        self.assertEqual(len(errors), 0)

        output = block.execute({})
        self.assertEqual(output.status, BlockStatus.COMPLETED)
        self.assertIn('dataframe', output.data)
        self.assertEqual(len(output.data['dataframe']), 500)

    def test_sample_size(self):
        block = DataSourceBlock('test-datasrc-sample')
        block.configure(
            data_source='synthetic',
            n_interactions=1000,
            sample_size=100
        )

        output = block.execute({})
        self.assertEqual(len(output.data['dataframe']), 100)


class TestSplitBlock(unittest.TestCase):
    """Test Split Block"""

    def test_random_split(self):
        # First create data
        data_block = DataSourceBlock('data')
        data_block.configure(data_source='synthetic', n_interactions=1000)
        data_output = data_block.execute({})

        # Then split
        split_block = SplitBlock('split')
        split_block.configure(test_size=0.2, method='random')

        output = split_block.execute({'dataframe': data_output.data['dataframe']})
        self.assertEqual(output.status, BlockStatus.COMPLETED)
        self.assertIn('train_data', output.data)
        self.assertIn('test_data', output.data)

        train_size = len(output.data['train_data'])
        test_size = len(output.data['test_data'])
        self.assertAlmostEqual(test_size / (train_size + test_size), 0.2, delta=0.05)


class TestPreprocessorBlock(unittest.TestCase):
    """Test Preprocessor Block"""

    def test_normalization(self):
        data_block = DataSourceBlock('data')
        data_block.configure(data_source='synthetic', n_interactions=100)
        data_output = data_block.execute({})

        preproc_block = PreprocessorBlock('preprocessor')
        preproc_block.configure(normalize=True)

        output = preproc_block.execute({'dataframe': data_output.data['dataframe']})
        self.assertEqual(output.status, BlockStatus.COMPLETED)
        self.assertIn('processed-data', output.data)


class TestCollaborativeFilteringBlock(unittest.TestCase):
    """Test Collaborative Filtering Block"""

    def test_user_based_cf(self):
        # Create and split data
        data_block = DataSourceBlock('data')
        data_block.configure(data_source='synthetic', n_users=20, n_items=30, n_interactions=200)
        data_output = data_block.execute({})

        split_block = SplitBlock('split')
        split_block.configure(test_size=0.2)
        split_output = split_block.execute({'dataframe': data_output.data['dataframe']})

        # Train CF model
        cf_block = CollaborativeFilteringBlock('cf')
        cf_block.configure(method='user-based')

        output = cf_block.execute({'split-data': split_output.data['split-data']})
        self.assertEqual(output.status, BlockStatus.COMPLETED)
        self.assertIn('model', output.data)


class TestMatrixFactorizationBlock(unittest.TestCase):
    """Test Matrix Factorization Block"""

    def test_svd_factorization(self):
        data_block = DataSourceBlock('data')
        data_block.configure(data_source='synthetic', n_users=20, n_items=30, n_interactions=200)
        data_output = data_block.execute({})

        split_block = SplitBlock('split')
        split_block.configure(test_size=0.2)
        split_output = split_block.execute({'dataframe': data_output.data['dataframe']})

        mf_block = MatrixFactorizationBlock('mf')
        mf_block.configure(method='svd', n_factors=10)

        output = mf_block.execute({'split-data': split_output.data['split-data']})
        self.assertEqual(output.status, BlockStatus.COMPLETED)
        self.assertIn('model', output.data)


class TestPredictionsBlock(unittest.TestCase):
    """Test Predictions Block"""

    def test_generate_predictions(self):
        # Create full pipeline
        data_block = DataSourceBlock('data')
        data_block.configure(data_source='synthetic', n_users=20, n_items=30, n_interactions=200)
        data_output = data_block.execute({})

        split_block = SplitBlock('split')
        split_block.configure(test_size=0.2)
        split_output = split_block.execute({'dataframe': data_output.data['dataframe']})

        cf_block = CollaborativeFilteringBlock('cf')
        cf_block.configure(method='user-based')
        cf_output = cf_block.execute({'split-data': split_output.data['split-data']})

        pred_block = PredictionsBlock('predictions')
        pred_block.configure(top_k=10)

        output = pred_block.execute({'model': cf_output.data['model']})
        self.assertEqual(output.status, BlockStatus.COMPLETED)
        self.assertIn('recommendations', output.data)


class TestEvaluationBlock(unittest.TestCase):
    """Test Evaluation Block"""

    def test_compute_metrics(self):
        # Create full pipeline
        data_block = DataSourceBlock('data')
        data_block.configure(data_source='synthetic', n_users=20, n_items=30, n_interactions=200)
        data_output = data_block.execute({})

        split_block = SplitBlock('split')
        split_block.configure(test_size=0.2)
        split_output = split_block.execute({'dataframe': data_output.data['dataframe']})

        cf_block = CollaborativeFilteringBlock('cf')
        cf_block.configure(method='user-based')
        cf_output = cf_block.execute({'split-data': split_output.data['split-data']})

        eval_block = EvaluationBlock('evaluation')
        eval_block.configure(metrics=['rmse', 'mae', 'precision'])

        output = eval_block.execute({'model': cf_output.data['model']})
        self.assertEqual(output.status, BlockStatus.COMPLETED)
        self.assertIn('metrics', output.data)
        self.assertIn('rmse', output.data['metrics'])


class TestFullPipeline(unittest.TestCase):
    """Test Complete Pipeline"""

    def test_complete_collaborative_filtering_pipeline(self):
        """Test: Data -> Split -> CF -> Predictions -> Evaluation"""

        # 1. Load data
        data_block = DataSourceBlock('data-source')
        data_block.configure(
            data_source='synthetic',
            n_users=50,
            n_items=100,
            n_interactions=500
        )
        data_output = data_block.execute({})
        self.assertEqual(data_output.status, BlockStatus.COMPLETED)

        # 2. Split data
        split_block = SplitBlock('split')
        split_block.configure(test_size=0.2, method='random')
        split_output = split_block.execute({'dataframe': data_output.data['dataframe']})
        self.assertEqual(split_output.status, BlockStatus.COMPLETED)

        # 3. Train model
        cf_block = CollaborativeFilteringBlock('collaborative-filtering')
        cf_block.configure(method='user-based')
        cf_output = cf_block.execute({'split-data': split_output.data['split-data']})
        self.assertEqual(cf_output.status, BlockStatus.COMPLETED)

        # 4. Generate predictions
        pred_block = PredictionsBlock('predictions')
        pred_block.configure(top_k=10)
        pred_output = pred_block.execute({'model': cf_output.data['model']})
        self.assertEqual(pred_output.status, BlockStatus.COMPLETED)

        # 5. Evaluate
        eval_block = EvaluationBlock('evaluation')
        eval_block.configure(metrics=['rmse', 'mae', 'precision', 'recall', 'ndcg'])
        eval_output = eval_block.execute({'model': cf_output.data['model']})
        self.assertEqual(eval_output.status, BlockStatus.COMPLETED)

        # Verify metrics
        metrics = eval_output.data['metrics']
        self.assertIn('rmse', metrics)
        self.assertGreater(metrics['rmse'], 0)

    def test_matrix_factorization_pipeline(self):
        """Test: Data -> Split -> MF -> Evaluation"""

        # 1. Load data
        data_block = DataSourceBlock('data')
        data_block.configure(data_source='synthetic', n_users=30, n_items=50, n_interactions=300)
        data_output = data_block.execute({})

        # 2. Split
        split_block = SplitBlock('split')
        split_block.configure(test_size=0.2)
        split_output = split_block.execute({'dataframe': data_output.data['dataframe']})

        # 3. Matrix factorization
        mf_block = MatrixFactorizationBlock('mf')
        mf_block.configure(method='svd', n_factors=10)
        mf_output = mf_block.execute({'split-data': split_output.data['split-data']})
        self.assertEqual(mf_output.status, BlockStatus.COMPLETED)

        # 4. Evaluate
        eval_block = EvaluationBlock('eval')
        eval_block.configure()
        eval_output = eval_block.execute({'model': mf_output.data['model']})
        self.assertEqual(eval_output.status, BlockStatus.COMPLETED)


if __name__ == '__main__':
    print("Running Mammoth Block Tests")
    print("=" * 70)
    unittest.main(verbosity=2)
