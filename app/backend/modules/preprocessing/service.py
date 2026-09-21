from pathlib import Path

import pandas as pd
from sqlalchemy.orm import Session

from app.backend.core.enums import ProjectStatus
from app.backend.modules.logs.service import LogService
from app.backend.modules.preprocessing.model import PreparedFeatures
from app.backend.modules.preprocessing.repository import PreprocessingRepository
from app.backend.modules.preprocessing.utility import (
    engineer_features,
    normalize_label_series,
    select_feature_columns,
)
from app.backend.modules.preprocessing.validation import ensure_feature_columns
from app.backend.modules.projects.service import ProjectService
from app.backend.utils.ml import build_preprocessor, feature_names, save_joblib_artifact, to_dense_array
from app.backend.utils.storage import read_dataframe, write_dataframe


class PreprocessingService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = PreprocessingRepository(session)
        self.log_service = LogService(session)

    def prepare(self, project_id: str) -> PreparedFeatures:
        dataset, cleaned = self.repository.latest_cleaned(project_id)
        if not dataset or not cleaned:
            raise ValueError("Run cleaning before preprocessing.")

        df = read_dataframe(Path(cleaned.cleaned_parquet_path))
        engineered_df, engineered_columns = engineer_features(df, dataset.schema_profile["semantic_columns"])
        feature_columns, numeric_columns, categorical_columns = select_feature_columns(
            engineered_df,
            dataset.schema_profile["semantic_columns"],
        )
        ensure_feature_columns(feature_columns)

        label_series = None
        if dataset.label_column and dataset.label_column in engineered_df.columns:
            label_series = normalize_label_series(engineered_df[dataset.label_column])

        preprocessor = build_preprocessor(numeric_columns, categorical_columns)
        matrix = preprocessor.fit_transform(engineered_df[feature_columns])
        dense_matrix = to_dense_array(matrix)
        transformer_path = save_joblib_artifact(project_id, "preprocessor", preprocessor)
        engineered_target = Path(cleaned.cleaned_parquet_path).with_name("engineered_dataset.parquet")
        write_dataframe(engineered_df, engineered_target)

        preprocessing_summary = {
            "original_feature_columns": feature_columns,
            "numeric_columns": numeric_columns,
            "categorical_columns": categorical_columns,
            "feature_names": feature_names(preprocessor),
            "label_column": dataset.label_column if label_series is not None else None,
            "transformer_path": str(transformer_path),
            "engineered_frame_path": str(engineered_target),
            "engineered_columns": engineered_columns,
        }
        cleaned.preprocessing_summary = preprocessing_summary
        project = ProjectService(self.session).repository.get(project_id)
        project.status = ProjectStatus.PREPROCESSED
        self.session.commit()
        self.log_service.record(
            "preprocessing.completed",
            "Feature preprocessing completed.",
            project_id=project_id,
            details=preprocessing_summary,
        )

        return PreparedFeatures(
            dataframe=engineered_df,
            feature_matrix=dense_matrix,
            feature_names=preprocessing_summary["feature_names"],
            original_feature_columns=feature_columns,
            numeric_columns=numeric_columns,
            categorical_columns=categorical_columns,
            label_column=preprocessing_summary["label_column"],
            label_series=label_series,
            transformer_path=str(transformer_path),
            engineered_frame_path=str(engineered_target),
        )
