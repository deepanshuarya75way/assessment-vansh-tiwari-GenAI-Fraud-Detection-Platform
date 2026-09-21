from __future__ import annotations

from collections import Counter
from typing import Any

import numpy as np
import pandas as pd


def top_counts(series: pd.Series | None, limit: int = 5) -> list[dict[str, Any]]:
    if series is None or series.empty:
        return []
    counts = Counter(series.fillna("unknown").astype(str))
    ordered = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return [{"label": label, "count": count} for label, count in ordered[:limit]]


def safe_numeric_series(series: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    return numeric.replace([np.inf, -np.inf], np.nan)


def build_time_buckets(df: pd.DataFrame, column: str | None) -> list[dict[str, Any]]:
    if not column or column not in df.columns:
        return []
    series = pd.to_datetime(df[column], errors="coerce", utc=True).dropna()
    if series.empty:
        return []
    grouped = series.dt.to_period("D").value_counts().sort_index()
    return [{"label": str(index), "count": int(value)} for index, value in grouped.items()]
