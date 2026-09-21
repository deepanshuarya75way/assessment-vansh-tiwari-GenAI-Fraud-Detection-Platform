from __future__ import annotations

from typing import Any

import numpy as np

from app.backend.modules.ml.utils import band_from_score, normalize_scores, threshold_summary


class RiskScoringEngine:
    def score(
        self,
        fraud_probabilities: np.ndarray | list[float],
        confidence_scores: np.ndarray | list[float],
        anomaly_scores: np.ndarray | list[float] | None = None,
    ) -> dict[str, Any]:
        probabilities = normalize_scores(fraud_probabilities)
        confidence = normalize_scores(confidence_scores)
        anomaly_component = normalize_scores(anomaly_scores) if anomaly_scores is not None else np.zeros_like(probabilities)

        risk_scores = np.clip((probabilities * 0.55) + ((1.0 - confidence) * 0.25) + (anomaly_component * 0.20), 0.0, 1.0) * 100.0
        normalized_scores = normalize_scores(risk_scores)
        risk_bands = [band_from_score(float(score)) for score in risk_scores]
        thresholds = threshold_summary(list(map(float, risk_scores)))
        return {
            "risk_scores": [round(float(score), 4) for score in risk_scores],
            "normalized_scores": [round(float(score), 4) for score in normalized_scores],
            "risk_bands": risk_bands,
            "thresholds": thresholds,
        }