from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import pandas as pd

from app.backend.agents.base import AgentContext, AgentLog, AgentResult, BaseAgent
from app.backend.core.exceptions import ProcessingError
from app.backend.utils.dataframe import dataframe_profile, load_dataframe


class ValidationAgent(BaseAgent):
    name = "validation_agent"

    async def execute(self, context: AgentContext) -> AgentResult:
        started_at = time.time()
        logs = [AgentLog(level="INFO", message="Loading uploaded dataset for structural validation.")]
        raw_path = context.input_data.get("raw_path")
        if not raw_path:
            raise ProcessingError("Validation agent requires a raw dataset path.")

        df = load_dataframe(Path(raw_path))
        if df.empty:
            raise ProcessingError("Uploaded dataset is empty.")

        profile = dataframe_profile(df)
        required_columns = list(context.configuration.get("required_columns", []))
        missing_required = [column for column in required_columns if column not in df.columns]
        data_quality_score = self._quality_score(df, profile)

        warnings: list[str] = []
        if profile["duplicate_rows"]:
            warnings.append(f"Detected {profile['duplicate_rows']} duplicate rows.")
        if profile["missing_by_column"]:
            warnings.append("Missing values detected in one or more columns.")

        payload = {
            "dataset_id": context.dataset_id,
            "row_count": profile["row_count"],
            "column_count": profile["column_count"],
            "semantic_columns": profile["semantic_columns"],
            "missing_by_column": profile["missing_by_column"],
            "duplicate_rows": profile["duplicate_rows"],
            "dtypes": profile["dtypes"],
            "missing_required_columns": missing_required,
            "invalid_values": [],
            "data_quality_score": data_quality_score,
            "preview_columns": profile["columns"][:12],
        }

        status = "success" if not missing_required else "warning"
        summary = "Dataset validated successfully." if status == "success" else "Dataset validated with schema warnings."
        return self._build_result(
            status=status,
            summary=summary,
            metadata={"dataset_id": context.dataset_id, "raw_path": raw_path},
            payload=payload,
            logs=logs,
            started_at=started_at,
            warnings=warnings,
            result_location=str(raw_path),
        )

    @staticmethod
    def _quality_score(df: pd.DataFrame, profile: dict[str, Any]) -> float:
        total_cells = max(int(df.shape[0] * df.shape[1]), 1)
        missing_cells = int(df.isna().sum().sum())
        duplicate_penalty = int(profile["duplicate_rows"])
        score = 100.0 - ((missing_cells / total_cells) * 60.0) - ((duplicate_penalty / max(len(df), 1)) * 40.0)
        return round(max(min(score, 100.0), 0.0), 2)