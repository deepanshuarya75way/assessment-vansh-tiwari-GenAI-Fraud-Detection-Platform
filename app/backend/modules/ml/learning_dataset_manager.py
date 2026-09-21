from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from app.backend.core.config import get_settings
from app.backend.modules.ml.artifacts import LearningDatasetArtifact
from app.backend.utils.storage import ensure_directory


class LearningDatasetManager:
    def __init__(self) -> None:
        self.settings = get_settings()

    def _history_path(self, dataset_id: str) -> Path:
        return self.settings.processed_directory / dataset_id / "learning_history.jsonl"

    def record_feedback(self, dataset_id: str, feedback_rows: list[dict[str, Any]]) -> LearningDatasetArtifact:
        history_path = self._history_path(dataset_id)
        ensure_directory(history_path.parent)
        with history_path.open("a", encoding="utf-8") as handle:
            for row in feedback_rows:
                handle.write(json.dumps(row, default=str) + "\n")

        retraining_df = self.build_retraining_dataset(dataset_id)
        retraining_path = self.settings.processed_directory / dataset_id / "retraining_dataset.parquet"
        ensure_directory(retraining_path.parent)
        retraining_df.to_parquet(retraining_path, index=False)

        statistics = {
            "feedback_rows": int(len(feedback_rows)),
            "retraining_rows": int(len(retraining_df)),
            "corrected_labels": retraining_df["corrected_label"].dropna().astype(str).value_counts().to_dict() if not retraining_df.empty else {},
        }
        return LearningDatasetArtifact(
            dataset_id=dataset_id,
            history_path=str(history_path),
            retraining_dataset_path=str(retraining_path),
            row_count=int(len(retraining_df)),
            statistics=statistics,
            metadata={"dataset_id": dataset_id},
        )

    def build_retraining_dataset(self, dataset_id: str) -> pd.DataFrame:
        history_path = self._history_path(dataset_id)
        if not history_path.exists():
            return pd.DataFrame(columns=["dataset_id", "result_id", "original_label", "corrected_label", "notes", "payload"])
        records: list[dict[str, Any]] = []
        with history_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    records.append(json.loads(line))
        return pd.DataFrame(records)