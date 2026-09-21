from __future__ import annotations

from collections import Counter
from typing import Any

import pandas as pd


def top_counts(series: pd.Series, limit: int = 10) -> list[dict[str, Any]]:
    counts = Counter(series.dropna().astype(str))
    return [{"label": label, "value": value} for label, value in counts.most_common(limit)]


def timeline_counts(df: pd.DataFrame, date_column: str | None) -> list[dict[str, Any]]:
    if not date_column or date_column not in df.columns or not pd.api.types.is_datetime64_any_dtype(df[date_column]):
        return []
    timeline = (
        df.assign(_period=df[date_column].dt.to_period("M").astype(str))
        .groupby("_period")
        .size()
        .reset_index(name="value")
    )
    return timeline.rename(columns={"_period": "label"}).to_dict(orient="records")


def risk_distribution(risks: list[float]) -> list[dict[str, Any]]:
    bins = {"0-25": 0, "26-50": 0, "51-75": 0, "76-100": 0}
    for score in risks:
        if score <= 25:
            bins["0-25"] += 1
        elif score <= 50:
            bins["26-50"] += 1
        elif score <= 75:
            bins["51-75"] += 1
        else:
            bins["76-100"] += 1
    return [{"label": key, "value": value} for key, value in bins.items()]
