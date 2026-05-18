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


SCRIPT_05 = load_script_module("05_build_country_year_dataset.py", "script_05_dataset")
SCRIPT_06 = load_script_module("06_audit_dataset_quality.py", "script_06_quality")
SCRIPT_07 = load_script_module("07_generate_eda_figures.py", "script_07_eda")


class StubWHOClient:
    def __init__(self, frame: pd.DataFrame):
        self.frame = frame

    def indicator_data(self, indicator_code: str) -> pd.DataFrame:
        return self.frame.copy()


class BuildCountryYearDatasetTests(unittest.TestCase):
    def test_normalize_one_indicator_rejects_multiple_non_preferred_dim1_values(self) -> None:
        client = StubWHOClient(
            pd.DataFrame(
                {
                    "SpatialDim": ["BRA", "BRA"],
                    "SpatialDimType": ["COUNTRY", "COUNTRY"],
                    "TimeDim": [2020, 2020],
                    "NumericValue": [70.0, 74.0],
                    "Dim1Type": ["SEX", "SEX"],
                    "Dim1": ["SEX_MLE", "SEX_FMLE"],
                }
            )
        )

        with self.assertRaises(ValueError):
            SCRIPT_05.normalize_one_indicator(client, "TEST_DIM1", "test_variable")

    def test_normalize_one_indicator_rejects_multiple_secondary_dimension_values(self) -> None:
        client = StubWHOClient(
            pd.DataFrame(
                {
                    "SpatialDim": ["BRA", "BRA"],
                    "SpatialDimType": ["COUNTRY", "COUNTRY"],
                    "TimeDim": [2020, 2020],
                    "NumericValue": [70.0, 74.0],
                    "Dim1Type": ["SEX", "SEX"],
                    "Dim1": ["Both sexes", "Both sexes"],
                    "Dim2Type": ["RESIDENCE", "RESIDENCE"],
                    "Dim2": ["URBAN", "RURAL"],
                }
            )
        )

        with self.assertRaises(ValueError):
            SCRIPT_05.normalize_one_indicator(client, "TEST_DIM2", "test_variable")

    def test_assign_variable_names_disambiguates_colliding_indicator_names(self) -> None:
        shortlist = pd.DataFrame(
            [
                {
                    "indicator_code": "GHED_GGHE-DCHE_SHA2011",
                    "indicator_name": "Domestic general government health expenditure (GGHE-D) as percentage of current health expenditure (CHE) (%)",
                },
                {
                    "indicator_code": "GHED_GGHE-DGGE_SHA2011",
                    "indicator_name": "Domestic general government health expenditure (GGHE-D) as percentage of general government expenditure (GGE) (%)",
                },
                {
                    "indicator_code": "GHED_GGHE-DGDP_SHA2011",
                    "indicator_name": "Domestic general government health expenditure (GGHE-D) as percentage of gross domestic product (GDP) (%)",
                },
            ]
        )

        named = SCRIPT_05.assign_variable_names(shortlist)

        self.assertEqual(named["variable_name"].nunique(), 3)
        self.assertNotIn("variable_name", shortlist.columns)


class AuditDatasetQualityTests(unittest.TestCase):
    def test_build_modeling_ready_dataset_keeps_variables_with_good_filtered_coverage(self) -> None:
        old_rows = [
            {
                "country_code": f"OLD{i}",
                "year": 1990 + i,
                "region_code": "AMR",
                "region": "Americas",
                "life_expectancy_at_birth": 60 + i,
                "feature_filtered_good": pd.NA,
                "feature_filtered_bad": pd.NA,
                "available_indicator_count": 1,
                "missing_indicator_count": 2,
                "data_completeness_score": 0.5,
            }
            for i in range(8)
        ]
        new_rows = [
            {
                "country_code": f"NEW{i}",
                "year": 2000 + i,
                "region_code": "AMR",
                "region": "Americas",
                "life_expectancy_at_birth": 70 + i,
                "feature_filtered_good": 10 + i,
                "feature_filtered_bad": pd.NA,
                "available_indicator_count": 2,
                "missing_indicator_count": 1,
                "data_completeness_score": 0.7,
            }
            for i in range(4)
        ]
        dataset = pd.DataFrame(old_rows + new_rows)
        missingness = SCRIPT_06.build_missingness_table(dataset, SCRIPT_06.get_indicator_columns(dataset))

        modeling = SCRIPT_06.build_modeling_ready_dataset(dataset, missingness)

        self.assertIn("feature_filtered_good", modeling.columns)
        self.assertNotIn("feature_filtered_bad", modeling.columns)


class GenerateEDAFiguresTests(unittest.TestCase):
    def test_resolve_scatter_candidates_uses_dictionary_codes(self) -> None:
        dictionary = pd.DataFrame(
            [
                {"indicator_code": "MDG_0000000007", "variable_name": "under_five_exact"},
                {"indicator_code": "MDG_0000000001", "variable_name": "infant_exact"},
                {"indicator_code": "WHOSIS_000003", "variable_name": "neonatal_exact"},
                {"indicator_code": "MDG_0000000026", "variable_name": "maternal_exact"},
                {"indicator_code": "WHS4_100", "variable_name": "immunization_exact"},
                {"indicator_code": "GHED_CHEGDP_SHA2011", "variable_name": "health_expenditure_exact"},
                {"indicator_code": "MDG_0000000017", "variable_name": "tuberculosis_exact"},
                {"indicator_code": "GHED_GGHE-DCHE_SHA2011", "variable_name": "health_expenditure_other"},
            ]
        )

        modeling_columns = [
            "life_expectancy_at_birth",
            "under_five_exact",
            "infant_exact",
            "neonatal_exact",
            "maternal_exact",
            "immunization_exact",
            "health_expenditure_exact",
            "health_expenditure_other",
            "tuberculosis_exact",
        ]

        resolved = dict(SCRIPT_07.resolve_scatter_candidates(modeling_columns, dictionary))

        self.assertEqual(resolved["health_expenditure"], "health_expenditure_exact")


if __name__ == "__main__":
    unittest.main()
