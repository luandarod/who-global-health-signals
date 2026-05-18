from __future__ import annotations

import unittest

import numpy as np
import pandas as pd

from src.models.benchmarking import build_surface_frame, build_temporal_cv, choose_surface_features, merge_model_artifacts


class BenchmarkingHelpersTest(unittest.TestCase):
    def test_build_temporal_cv_uses_forward_only_validation_blocks(self) -> None:
        frame = pd.DataFrame(
            {
                'year': [2000, 2000, 2001, 2001, 2002, 2002, 2003, 2003, 2004, 2004],
                'life_expectancy_at_birth': [60, 61, 62, 63, 64, 65, 66, 67, 68, 69],
                'feature_a': range(10),
                'region': ['A'] * 10,
            }
        )

        splits = build_temporal_cv(frame, n_splits=3)

        self.assertEqual(len(splits), 3)
        for train_idx, val_idx in splits:
            train_years = frame.iloc[train_idx]['year']
            val_years = frame.iloc[val_idx]['year']
            self.assertLess(train_years.max(), val_years.min())
            self.assertGreater(len(train_idx), 0)
            self.assertGreater(len(val_idx), 0)

    def test_choose_surface_features_prefers_ranked_numeric_features(self) -> None:
        frame = pd.DataFrame(
            {
                'country_code': ['A', 'B', 'C', 'D'],
                'year': [2016, 2017, 2018, 2019],
                'region': ['R1', 'R1', 'R2', 'R2'],
                'life_expectancy_at_birth': [70.0, 71.5, 73.0, 74.0],
                'under5_mortality': [40.0, 35.0, 20.0, 18.0],
                'immunization_rate': [70.0, 72.0, 85.0, 88.0],
                'data_completeness_score': [0.4, 0.5, 0.8, 0.9],
            }
        )
        importance = pd.DataFrame(
            {
                'feature': ['region_R1', 'under5_mortality', 'immunization_rate', 'data_completeness_score'],
                'importance': [0.9, 0.8, 0.7, 0.6],
            }
        )

        feature_x, feature_y = choose_surface_features(frame, importance)

        self.assertEqual((feature_x, feature_y), ('under5_mortality', 'immunization_rate'))

    def test_merge_model_artifacts_preserves_optional_reference_rows(self) -> None:
        local_metrics = pd.DataFrame([{'model': 'lightgbm', 'test_mae': 1.8}])
        local_predictions = pd.DataFrame([{'model': 'lightgbm', 'abs_error': 1.8}])
        external_metrics = pd.DataFrame([{'model': 'tabpfn_priorlabs', 'test_mae': 0.9}])
        external_predictions = pd.DataFrame([{'model': 'tabpfn_priorlabs', 'abs_error': 0.9}])

        comparison, all_predictions = merge_model_artifacts(
            local_metrics,
            local_predictions,
            external_metrics,
            external_predictions,
        )

        self.assertEqual(comparison['model'].tolist(), ['tabpfn_priorlabs', 'lightgbm'])
        self.assertEqual(set(all_predictions['model'].tolist()), {'lightgbm', 'tabpfn_priorlabs'})

    def test_build_surface_frame_masks_points_far_from_observed_support(self) -> None:
        class DummyModel:
            def predict(self, frame: pd.DataFrame) -> np.ndarray:
                return frame['feature_x'].to_numpy(dtype=float) + frame['feature_y'].to_numpy(dtype=float)

        frame = pd.DataFrame(
            {
                'country_code': ['A', 'B', 'C', 'D', 'E', 'F'],
                'year': [2010, 2011, 2012, 2013, 2014, 2014],
                'region': ['R1'] * 6,
                'life_expectancy_at_birth': [60.0, 61.0, 62.0, 63.0, 64.0, 65.0],
                'feature_x': [0.0, 0.0, 0.02, 1.0, 1.0, 1.02],
                'feature_y': [0.0, 0.02, 0.0, 1.0, 1.02, 1.0],
            }
        )

        surface, meta = build_surface_frame(
            DummyModel(),
            frame,
            feature_x='feature_x',
            feature_y='feature_y',
            grid_size=10,
        )

        self.assertGreater(meta['masked_share'], 0.0)
        self.assertTrue(surface['predicted'].isna().any())


if __name__ == '__main__':
    unittest.main()
