from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pandas as pd


@dataclass(slots=True)
class FeatureEngineeringArtifact:
    dataset_id: str
    feature_frame: pd.DataFrame
    engineered_columns: list[str]
    removed_columns: list[str]
    report: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    errors: list[dict[str, Any]] = field(default_factory=list)


@dataclass(slots=True)
class FeatureSelectionArtifact:
    dataset_id: str
    selected_feature_frame: pd.DataFrame
    selected_columns: list[str]
    feature_importance: list[dict[str, Any]]
    report: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    errors: list[dict[str, Any]] = field(default_factory=list)


@dataclass(slots=True)
class EvaluationArtifact:
    dataset_id: str
    model_name: str
    metrics: dict[str, Any]
    confusion_matrix: list[list[int]] | None
    class_labels: list[str]
    per_class_metrics: dict[str, Any]
    summary: str
    metadata: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    errors: list[dict[str, Any]] = field(default_factory=list)


@dataclass(slots=True)
class ModelArtifact:
    dataset_id: str
    model_name: str
    model_kind: str
    model_version: str
    model_path: str
    metadata_path: str
    feature_columns: list[str]
    metrics: dict[str, Any]
    metadata: dict[str, Any]
    training_time_seconds: float
    warnings: list[str] = field(default_factory=list)
    errors: list[dict[str, Any]] = field(default_factory=list)


@dataclass(slots=True)
class ModelTrainingArtifact:
    dataset_id: str
    model_name: str
    model_kind: str
    model_version: str
    training_status: str
    feature_columns: list[str]
    metrics: dict[str, Any]
    evaluation: EvaluationArtifact | None
    model_path: str
    metadata_path: str
    training_time_seconds: float
    metadata: dict[str, Any]
    warnings: list[str] = field(default_factory=list)
    errors: list[dict[str, Any]] = field(default_factory=list)


@dataclass(slots=True)
class PredictionRecord:
    row_identifier: str
    predicted_label: str
    fraud_probability: float
    confidence_score: float
    normalized_risk_score: float
    risk_band: str
    model_name: str
    explanation: str | None
    explanation_payload: dict[str, Any] | None
    prediction_metadata: dict[str, Any]


@dataclass(slots=True)
class FraudDetectionArtifact:
    dataset_id: str
    model_name: str
    model_kind: str
    model_version: str
    predictions: list[PredictionRecord]
    summary: dict[str, Any]
    risk_distribution: dict[str, int]
    confidence_scores: list[float]
    feature_importance: list[dict[str, Any]]
    metadata: dict[str, Any]
    result_location: str | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[dict[str, Any]] = field(default_factory=list)


@dataclass(slots=True)
class LearningDatasetArtifact:
    dataset_id: str
    history_path: str
    retraining_dataset_path: str
    row_count: int
    statistics: dict[str, Any]
    metadata: dict[str, Any]
    warnings: list[str] = field(default_factory=list)
    errors: list[dict[str, Any]] = field(default_factory=list)