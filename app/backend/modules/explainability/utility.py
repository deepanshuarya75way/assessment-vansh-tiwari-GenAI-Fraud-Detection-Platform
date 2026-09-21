from __future__ import annotations

from typing import Any

import pandas as pd

from app.backend.utils.dataframe import frequency_scores, robust_z_scores


def build_score_maps(df: pd.DataFrame) -> dict[str, pd.Series]:
    score_maps: dict[str, pd.Series] = {}
    for column in df.columns:
        if pd.api.types.is_numeric_dtype(df[column]):
            score_maps[column] = robust_z_scores(df[column]).abs()
        elif pd.api.types.is_datetime64_any_dtype(df[column]):
            hour_series = df[column].dt.hour.fillna(-1)
            score_maps[column] = frequency_scores(hour_series.astype(str))
        else:
            score_maps[column] = frequency_scores(df[column])
    return score_maps


def explanation_reason(feature: str, value: Any, baseline: Any) -> str:
    if isinstance(value, (int, float)) and isinstance(baseline, (int, float)):
        return f"{feature} deviates from the dataset baseline ({baseline}) with observed value {round(value, 4)}."
    return f"{feature} is uncommon for this uploaded dataset, with observed value '{value}'."
