from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score

from app.backend.modules.ml.artifacts import EvaluationArtifact


class ModelEvaluationEngine:
    def evaluate(
        self,
        dataset_id: str,
        model_name: str,
        y_true: list[int] | np.ndarray | None,
        y_pred: list[int] | np.ndarray,
        y_prob: list[float] | np.ndarray | None = None,
    ) -> EvaluationArtifact:
        metrics: dict[str, Any] = {}
        per_class_metrics: dict[str, Any] = {}
        confusion: list[list[int]] | None = None
        labels = ["safe", "fraud"]

        if y_true is not None and len(np.unique(y_true)) >= 2:
            metrics = {
                "accuracy": float(accuracy_score(y_true, y_pred)),
                "precision": float(precision_score(y_true, y_pred, zero_division=0)),
                "recall": float(recall_score(y_true, y_pred, zero_division=0)),
                "f1_score": float(f1_score(y_true, y_pred, zero_division=0)),
            }
            if y_prob is not None:
                try:
                    metrics["roc_auc"] = float(roc_auc_score(y_true, y_prob))
                except Exception:
                    metrics["roc_auc"] = None
            confusion = confusion_matrix(y_true, y_pred).tolist()
            per_class_metrics = {"positive_class": "fraud", "sample_count": int(len(y_true))}
            summary = (
                f"Accuracy {metrics['accuracy']:.3f}, Precision {metrics['precision']:.3f}, "
                f"Recall {metrics['recall']:.3f}, F1 {metrics['f1_score']:.3f}."
            )
        else:
            metrics = {"status": "unlabeled_dataset", "sample_count": int(len(y_pred))}
            summary = "Evaluation metrics are limited because the uploaded dataset does not contain reliable labels."

        return EvaluationArtifact(
            dataset_id=dataset_id,
            model_name=model_name,
            metrics=metrics,
            confusion_matrix=confusion,
            class_labels=labels,
            per_class_metrics=per_class_metrics,
            summary=summary,
            metadata={"has_labels": y_true is not None},
        )