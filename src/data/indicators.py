"""Initial WHO GHO indicator plan.

The codes below are a starting point for exploration. They must be validated
against API availability, country coverage and temporal completeness before the
final modeling dataset is built.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class IndicatorCandidate:
    code: str
    theme: str
    role: str
    notes: str


INITIAL_INDICATOR_CANDIDATES: list[IndicatorCandidate] = [
    IndicatorCandidate(
        code="WHOSIS_000001",
        theme="outcome",
        role="target",
        notes="Life expectancy at birth. Main regression target.",
    ),
    # The remaining indicators will be confirmed during API exploration.
    # Keep this file as the controlled shortlist rather than pulling the full
    # WHO indicator catalog into the modeling dataset.
]


TARGET_INDICATOR = "WHOSIS_000001"
