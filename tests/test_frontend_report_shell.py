from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_script_module(filename: str, module_name: str):
    path = PROJECT_ROOT / "scripts" / filename
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


SCRIPT_11 = load_script_module("11_export_report_assets.py", "script_11_report_assets")
SCRIPT_12 = load_script_module("12_prepare_web_assets.py", "script_12_web_assets")


class ReportAssetTests(unittest.TestCase):
    def test_align_executive_findings_tracks_best_model(self) -> None:
        executive = pd.DataFrame(
            [
                {"finding_id": "champion_model", "metric": "ridge", "value": 0.24},
                {"finding_id": "overall_error", "metric": "mean_absolute_error", "value": 0.24},
            ]
        )
        comparison = pd.DataFrame(
            [
                {"model": "tabpfn_priorlabs", "test_mae": 0.11},
                {"model": "ridge", "test_mae": 0.24},
            ]
        )

        aligned = SCRIPT_11.align_executive_findings(executive, comparison)
        champion = aligned.loc[aligned["finding_id"] == "champion_model"].iloc[0]
        overall = aligned.loc[aligned["finding_id"] == "overall_error"].iloc[0]

        self.assertEqual(champion["metric"], "tabpfn_priorlabs")
        self.assertAlmostEqual(champion["value"], 0.11)
        self.assertAlmostEqual(overall["value"], 0.11)

    def test_prepare_web_assets_includes_champion_scatter_payload(self) -> None:
        self.assertIn("champion_predictions.json", SCRIPT_12.REQUIRED_FILES)


class FrontendShellTests(unittest.TestCase):
    def test_index_routes_to_new_report_home(self) -> None:
        source = (PROJECT_ROOT / "web" / "src" / "pages" / "index.astro").read_text(encoding="utf-8")
        self.assertIn("import ReportHome from '../components/ReportHome.astro';", source)
        self.assertIn("<ReportHome />", source)

    def test_report_home_references_glossary_and_native_charts(self) -> None:
        source = (PROJECT_ROOT / "web" / "src" / "components" / "ReportHome.astro").read_text(encoding="utf-8")
        self.assertIn("<GlossaryTerm term=\"mae\"", source)
        self.assertIn("CountryCaseExplorer", source)
        self.assertIn("ExecutiveSummary", source)
        self.assertIn("ResponseSurfaceHeatmap", source)
        self.assertNotIn("/figures/", source)


if __name__ == "__main__":
    unittest.main()
