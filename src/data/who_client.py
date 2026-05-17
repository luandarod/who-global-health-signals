"""WHO Global Health Observatory OData API client.

This module contains small, explicit functions for exploring the WHO GHO API
and downloading indicator data. It is intentionally lightweight so the first
notebooks can inspect raw responses before the project introduces heavier
abstractions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd
import requests


DEFAULT_BASE_URL = "https://ghoapi.azureedge.net/api"


@dataclass(frozen=True)
class WHOGHOClient:
    """Minimal client for the WHO GHO OData API."""

    base_url: str = DEFAULT_BASE_URL
    timeout: int = 60

    def _url(self, path: str) -> str:
        clean_path = path.strip("/")
        return f"{self.base_url.rstrip('/')}/{clean_path}"

    def get_json(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Return raw JSON from an API path."""
        response = requests.get(self._url(path), params=params, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def get_values(self, path: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Return the OData `value` payload from an API path."""
        data = self.get_json(path=path, params=params)
        values = data.get("value", [])
        if not isinstance(values, list):
            raise TypeError("Expected OData response field 'value' to be a list.")
        return values

    def get_dataframe(self, path: str, params: dict[str, Any] | None = None) -> pd.DataFrame:
        """Return an API path as a pandas DataFrame."""
        return pd.DataFrame(self.get_values(path=path, params=params))

    def indicators(self) -> pd.DataFrame:
        """List available indicators."""
        return self.get_dataframe("Indicator")

    def dimensions(self) -> pd.DataFrame:
        """List available dimensions."""
        return self.get_dataframe("Dimension")

    def dimension_values(self, dimension_code: str) -> pd.DataFrame:
        """List values for a specific dimension, for example COUNTRY or REGION."""
        return self.get_dataframe(f"Dimension/{dimension_code}/DimensionValues")

    def indicator_data(
        self,
        indicator_code: str,
        *,
        top: int | None = None,
        filter_expression: str | None = None,
    ) -> pd.DataFrame:
        """Download data for one WHO indicator.

        Parameters
        ----------
        indicator_code:
            WHO GHO indicator code, for example WHOSIS_000001 for life expectancy at birth.
        top:
            Optional OData `$top` limit for quick API exploration.
        filter_expression:
            Optional OData `$filter` expression.
        """
        params: dict[str, Any] = {}
        if top is not None:
            params["$top"] = top
        if filter_expression:
            params["$filter"] = filter_expression
        return self.get_dataframe(indicator_code, params=params or None)


def normalize_indicator_frame(frame: pd.DataFrame, value_column: str = "NumericValue") -> pd.DataFrame:
    """Return a compact version of a WHO indicator frame.

    The WHO API can return many metadata columns. This helper keeps the fields
    that are most useful for the first country-year analytical dataset.
    """
    if frame.empty:
        return frame.copy()

    preferred_columns = [
        "IndicatorCode",
        "Indicator",
        "SpatialDimType",
        "SpatialDim",
        "ParentLocationCode",
        "ParentLocation",
        "TimeDimType",
        "TimeDim",
        "Dim1Type",
        "Dim1",
        value_column,
        "Low",
        "High",
        "Comments",
    ]
    available = [column for column in preferred_columns if column in frame.columns]
    compact = frame.loc[:, available].copy()

    if "TimeDim" in compact.columns:
        compact["TimeDim"] = pd.to_numeric(compact["TimeDim"], errors="coerce").astype("Int64")
    if value_column in compact.columns:
        compact[value_column] = pd.to_numeric(compact[value_column], errors="coerce")

    return compact


if __name__ == "__main__":
    client = WHOGHOClient()
    sample = client.indicator_data("WHOSIS_000001", top=5)
    print(normalize_indicator_frame(sample).head())
