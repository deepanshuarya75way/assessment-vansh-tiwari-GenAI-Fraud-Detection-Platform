from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import pandas as pd

from app.backend.agents.base import AgentContext, AgentLog, AgentResult, BaseAgent
from app.backend.core.exceptions import ProcessingError
from app.backend.utils.dataframe import coerce_datetime_columns, coerce_numeric_candidates, infer_semantic_columns, normalize_columns
from app.backend.utils.storage import write_dataframe


class CleaningAgent(BaseAgent):
    name = "cleaning_agent"

    async def execute(self, context: AgentContext) -> AgentResult:
        started_at = time.time()
        logs = [AgentLog(level="INFO", message="Applying deterministic cleaning transformations.")]
        raw_path = context.input_data.get("raw_path")
        if not raw_path:
            raise ProcessingError("Cleaning agent requires a raw dataset path.")

        df = pd.read_parquet(Path(raw_path)) if str(raw_path).endswith(".parquet") else pd.read_csv(Path(raw_path))
        original_rows = len(df)
        df = normalize_columns(df)
        df = coerce_numeric_candidates(df)
        semantic_columns = infer_semantic_columns(df)
        df = coerce_datetime_columns(df, semantic_columns)
        before_dedup = len(df)
        df = df.drop_duplicates().reset_index(drop=True)
        duplicates_removed = before_dedup - len(df)

        missing_filled: dict[str, int] = {}
        for column in df.columns:
            missing_count = int(df[column].isna().sum())
            if not missing_count:
                continue
            missing_filled[column] = missing_count
            if pd.api.types.is_numeric_dtype(df[column]):
                df[column] = df[column].fillna(df[column].median())
            else:
                df[column] = df[column].fillna("unknown")

        cleaned_path = context.input_data.get("cleaned_path")
        if not cleaned_path:
            raise ProcessingError("Cleaning agent requires a cleaned dataset output path.")

        cleaned_target = Path(cleaned_path)
        write_dataframe(df, cleaned_target)

        payload = {
            "dataset_id": context.dataset_id,
            "rows_before": original_rows,
            "rows_after": len(df),
            "duplicates_removed": duplicates_removed,
            "missing_filled": missing_filled,
            "normalized_columns": list(df.columns),
            "semantic_columns": semantic_columns,
            "cleaned_path": str(cleaned_target),
        }
        return self._build_result(
            status="success",
            summary="Dataset cleaned and normalized.",
            metadata={"dataset_id": context.dataset_id, "raw_path": str(raw_path)},
            payload=payload,
            logs=logs,
            started_at=started_at,
            result_location=str(cleaned_target),
        )