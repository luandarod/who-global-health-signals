from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_script_module(filename: str, module_name: str):
    path = PROJECT_ROOT / "scripts" / filename
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


SCRIPT_10 = load_script_module("10_analyze_model_residuals.py", "script_10_residuals")
SCRIPT_08 = load_script_module("08_train_baseline_models.py", "script_08_benchmark")


class ResidualOutputNamingTests(unittest.TestCase):
    def test_champion_figure_filenames_are_generic(self) -> None:
        self.assertEqual(SCRIPT_08.CHAMPION_FIGURE_NAMES["actual_vs_predicted"], "06_champion_actual_vs_predicted.png")
        self.assertEqual(SCRIPT_08.CHAMPION_FIGURE_NAMES["region_error"], "07_champion_residuals_by_region.png")
        self.assertEqual(SCRIPT_08.CHAMPION_FIGURE_NAMES["importance"], "08_champion_feature_importance.png")

    def test_residual_figure_filenames_are_generic(self) -> None:
        self.assertEqual(SCRIPT_10.RESIDUAL_FIGURE_NAMES["region"], "11_residuals_by_region.png")
        self.assertEqual(SCRIPT_10.RESIDUAL_FIGURE_NAMES["year"], "12_residuals_by_year.png")
        self.assertEqual(SCRIPT_10.RESIDUAL_FIGURE_NAMES["country"], "13_top_country_residuals.png")


if __name__ == "__main__":
    unittest.main()
