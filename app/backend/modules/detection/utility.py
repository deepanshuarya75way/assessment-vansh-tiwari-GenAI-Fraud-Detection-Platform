from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.metrics import precision_recall_fscore_support, roc_auc_score


def normalize_scores(values: np.ndarray) -> np.ndarray:
    minimum = float(values.min())
    maximum = float(values.max())
    if maximum - minimum <= 1e-9:
        return np.full_like(values, 0.5, dtype=float)
    return (values - minimum) / (maximum - minimum)


def default_contamination(sample_size: int) -> float:
    return float(min(0.15, max(0.02, 2 / max(sample_size**0.5, 1))))


def label_from_risk(risk_scores: np.ndarray, fraud_threshold: float, review_threshold: float) -> list[str]:
    labels: list[str] = []
    for value in risk_scores:
        if value >= fraud_threshold:
            labels.append("fraud")
        elif value >= review_threshold:
            labels.append("review")
        else:
            labels.append("safe")
    return labels


def supervised_metrics(y_true: np.ndarray, probabilities: np.ndarray) -> dict[str, Any]:
    predictions = (probabilities >= 0.5).astype(int)
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true,
        predictions,
        average="binary",
        zero_division=0,
    )
    payload: dict[str, Any] = {
        "precision": float(precision),
        "recall": float(recall),
        "f1_score": float(f1),
    }
    if len(set(y_true.tolist())) > 1:
        payload["roc_auc"] = float(roc_auc_score(y_true, probabilities))
    return payload
