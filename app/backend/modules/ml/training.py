from __future__ import annotations

import time
from typing import Any

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from app.backend.modules.ml.artifacts import ModelTrainingArtifact
from app.backend.modules.ml.evaluation import ModelEvaluationEngine
from app.backend.modules.ml.feature_selection import FeatureSelectionEngine
from app.backend.modules.ml.model_factory import ModelFactory, ModelSpec
from app.backend.modules.ml.model_manager import ModelManager


class FraudModelTrainer:
    def __init__(self, model_factory: ModelFactory | None = None, model_manager: ModelManager | None = None) -> None:
        self.model_factory = model_factory or ModelFactory()
        self.model_manager = model_manager or ModelManager()
        self.evaluator = ModelEvaluationEngine()
        self.selection_engine = FeatureSelectionEngine()

    def train(
        self,
        dataset_id: str,
        feature_frame: pd.DataFrame,
        semantic_columns: dict[str, str | None],
        labels: pd.Series | None = None,
        model_name: str = "random_forest",
        config: dict[str, Any] | None = None,
    ) -> ModelTrainingArtifact:
        started_at = time.time()
        selection = self.selection_engine.select(dataset_id, feature_frame, semantic_columns, labels)
        X = selection.selected_feature_frame
        feature_columns = selection.selected_columns

        if labels is not None and labels.nunique(dropna=True) >= 2:
            model = self.model_factory.create(ModelSpec(name=model_name, kind="supervised", config=config or {}))
            y = labels.astype(int)
            stratify = y if y.nunique() > 1 else None
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=stratify)
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            y_prob = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else None
            evaluation = self.evaluator.evaluate(dataset_id, model_name, y_test, y_pred, y_prob)
            training_status = "supervised_trained"
            model_kind = "supervised"
        else:
            model_name = model_name if model_name == "isolation_forest" else "isolation_forest"
            model = self.model_factory.create(ModelSpec(name=model_name, kind="unsupervised", config=config or {}))
            model.fit(X)
            anomaly_scores = -model.score_samples(X) if hasattr(model, "score_samples") else -model.decision_function(X)
            pseudo_labels = (anomaly_scores >= np.quantile(anomaly_scores, 0.9)).astype(int)
            evaluation = self.evaluator.evaluate(dataset_id, model_name, None, pseudo_labels, None)
            training_status = "unsupervised_trained"
            model_kind = "unsupervised"

        artifact = self.model_manager.register_model(
            dataset_id=dataset_id,
            model_name=model_name,
            model_kind=model_kind,
            estimator=model,
            feature_columns=feature_columns,
            metrics=evaluation.metrics,
            metadata={
                "selection_report": selection.report,
                "selection_metadata": selection.metadata,
                "training_status": training_status,
                "model_kind": model_kind,
            },
            training_time_seconds=round(time.time() - started_at, 4),
        )
        return ModelTrainingArtifact(
            dataset_id=dataset_id,
            model_name=model_name,
            model_kind=model_kind,
            model_version=artifact.model_version,
            training_status=training_status,
            feature_columns=feature_columns,
            metrics=evaluation.metrics,
            evaluation=evaluation,
            model_path=artifact.model_path,
            metadata_path=artifact.metadata_path,
            training_time_seconds=artifact.training_time_seconds,
            metadata=artifact.metadata,
        )