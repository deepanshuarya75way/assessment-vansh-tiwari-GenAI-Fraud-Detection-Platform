from __future__ import annotations

import time
from pathlib import Path

import pandas as pd

from app.backend.agents.base import AgentContext, AgentLog, AgentResult, BaseAgent
from app.backend.core.exceptions import ProcessingError
from app.backend.modules.preprocessing.utility import engineer_features, normalize_label_series, select_feature_columns
from app.backend.utils.ml import build_preprocessor, feature_names, save_joblib_artifact, to_dense_array
from app.backend.utils.storage import write_dataframe


class PreprocessingAgent(BaseAgent):
    name = "preprocessing_agent"

    async def execute(self, context: AgentContext) -> AgentResult:
        started_at = time.time()
        logs = [AgentLog(level="INFO", message="Generating ML-ready feature matrix.")]
        cleaned_path = context.input_data.get("cleaned_path")
        if not cleaned_path:
            raise ProcessingError("Preprocessing agent requires a cleaned dataset path.")

        df = pd.read_parquet(Path(cleaned_path))
        semantic_columns = context.input_data.get("semantic_columns") or {}
        engineered_df, engineered_columns = engineer_features(df, semantic_columns)
        feature_columns, numeric_columns, categorical_columns = select_feature_columns(engineered_df, semantic_columns)
        if not feature_columns:
            raise ProcessingError("No usable feature columns were derived from the uploaded dataset.")

        label_series = None
        label_column = semantic_columns.get("label")
        if label_column and label_column in engineered_df.columns:
            label_series = normalize_label_series(engineered_df[label_column])

        preprocessor = build_preprocessor(numeric_columns, categorical_columns)
        matrix = preprocessor.fit_transform(engineered_df[feature_columns])
        dense_matrix = to_dense_array(matrix)
        transformer_path = save_joblib_artifact(context.dataset_id, "preprocessor", preprocessor)
        engineered_path = context.input_data.get("engineered_path") or str(Path(cleaned_path).with_name("engineered_dataset.parquet"))
        write_dataframe(engineered_df, Path(engineered_path))

        payload = {
            "dataset_id": context.dataset_id,
            "feature_columns": feature_columns,
            "numeric_columns": numeric_columns,
            "categorical_columns": categorical_columns,
            "feature_names": feature_names(preprocessor),
            "label_column": label_column if label_series is not None else None,
            "engineered_columns": engineered_columns,
            "engineered_path": str(engineered_path),
            "transformer_path": str(transformer_path),
            "feature_matrix_shape": [int(dense_matrix.shape[0]), int(dense_matrix.shape[1])],
        }
        return self._build_result(
            status="success",
            summary="Feature engineering and preprocessing completed.",
            metadata={"dataset_id": context.dataset_id, "cleaned_path": str(cleaned_path)},
            payload=payload,
            logs=logs,
            started_at=started_at,
            result_location=str(engineered_path),
        )