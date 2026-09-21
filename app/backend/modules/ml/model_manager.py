from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

import joblib

from app.backend.core.config import get_settings
from app.backend.modules.ml.artifacts import ModelArtifact
from app.backend.utils.storage import ensure_directory, write_json


class ModelManager:
    def __init__(self) -> None:
        self.settings = get_settings()

    def _model_directory(self, dataset_id: str, model_name: str, model_version: str) -> Path:
        return self.settings.model_directory / dataset_id / model_name / model_version

    def register_model(
        self,
        *,
        dataset_id: str,
        model_name: str,
        model_kind: str,
        estimator: Any,
        feature_columns: list[str],
        metrics: dict[str, Any],
        metadata: dict[str, Any],
        model_version: str | None = None,
        training_time_seconds: float = 0.0,
    ) -> ModelArtifact:
        version = model_version or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + f"_{uuid4().hex[:8]}"
        model_dir = ensure_directory(self._model_directory(dataset_id, model_name, version))
        model_path = model_dir / "model.joblib"
        metadata_path = model_dir / "metadata.json"

        joblib.dump(estimator, model_path)
        payload = {
            "dataset_id": dataset_id,
            "model_name": model_name,
            "model_kind": model_kind,
            "model_version": version,
            "feature_columns": feature_columns,
            "metrics": metrics,
            "metadata": metadata,
            "training_time_seconds": training_time_seconds,
        }
        write_json(metadata_path, payload)

        return ModelArtifact(
            dataset_id=dataset_id,
            model_name=model_name,
            model_kind=model_kind,
            model_version=version,
            model_path=str(model_path),
            metadata_path=str(metadata_path),
            feature_columns=feature_columns,
            metrics=metrics,
            metadata=metadata,
            training_time_seconds=training_time_seconds,
        )

    def load_model(self, artifact: ModelArtifact) -> Any:
        return joblib.load(artifact.model_path)

    def list_model_versions(self, dataset_id: str, model_name: str) -> list[str]:
        model_dir = self.settings.model_directory / dataset_id / model_name
        if not model_dir.exists():
            return []
        return sorted([path.name for path in model_dir.iterdir() if path.is_dir()])

    def latest_model_path(self, dataset_id: str, model_name: str) -> Path | None:
        versions = self.list_model_versions(dataset_id, model_name)
        if not versions:
            return None
        return self.settings.model_directory / dataset_id / model_name / versions[-1] / "model.joblib"