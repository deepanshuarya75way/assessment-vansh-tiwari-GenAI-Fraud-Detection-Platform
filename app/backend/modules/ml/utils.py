from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import numpy as np


def iter_batches(length: int, batch_size: int) -> Iterable[tuple[int, int]]:
    batch_size = max(int(batch_size), 1)
    for start in range(0, length, batch_size):
        yield start, min(start + batch_size, length)


def normalize_scores(scores: np.ndarray | list[float]) -> np.ndarray:
    values = np.asarray(scores, dtype=float)
    if values.size == 0:
        return values
    min_value = np.nanmin(values)
    max_value = np.nanmax(values)
    if np.isclose(min_value, max_value):
        return np.zeros_like(values, dtype=float)
    normalized = (values - min_value) / (max_value - min_value)
    return np.nan_to_num(normalized, nan=0.0, posinf=1.0, neginf=0.0)


def band_from_score(score: float) -> str:
    if score >= 75:
        return "high"
    if score >= 45:
        return "medium"
    return "low"


def threshold_summary(scores: list[float]) -> dict[str, float]:
    values = np.asarray(scores, dtype=float)
    if values.size == 0:
        return {"low": 0.0, "medium": 0.0, "high": 0.0}
    return {
        "low": float(np.quantile(values, 0.33)),
        "medium": float(np.quantile(values, 0.66)),
        "high": float(np.quantile(values, 0.90)),
    }


def summarize_top_features(feature_importance: dict[str, float], limit: int = 20) -> list[dict[str, Any]]:
    ordered = sorted(feature_importance.items(), key=lambda item: (-item[1], item[0]))
    return [{"feature": feature, "importance": round(float(score), 6)} for feature, score in ordered[:limit]]