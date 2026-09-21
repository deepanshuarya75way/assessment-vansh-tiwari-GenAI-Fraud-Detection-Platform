from __future__ import annotations

from typing import Any

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import VarianceThreshold
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from app.backend.modules.ml.artifacts import FeatureSelectionArtifact
from app.backend.modules.ml.utils import summarize_top_features


class FeatureSelectionEngine:
    def __init__(self, *, top_k: int | None = None) -> None:
        self.top_k = top_k

    def select(
        self,
        dataset_id: str,
        frame: pd.DataFrame,
        semantic_columns: dict[str, str | None],
        labels: pd.Series | None = None,
    ) -> FeatureSelectionArtifact:
        excluded = {value for key, value in semantic_columns.items() if key in {"label", "transaction_id"} and value}
        candidate_columns = [column for column in frame.columns if column not in excluded]
        if not candidate_columns:
            raise ValueError("No usable feature columns are available for feature selection.")

        numeric_columns = frame[candidate_columns].select_dtypes(include=["number"]).columns.tolist()
        categorical_columns = [
            column
            for column in candidate_columns
            if column not in numeric_columns and frame[column].dtype.name in {"object", "string", "category", "bool"}
        ]

        numeric_pipeline = Pipeline([("imputer", SimpleImputer(strategy="median"))])
        categorical_pipeline = Pipeline(
            [
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
            ]
        )

        if numeric_columns:
            numeric_frame = pd.DataFrame(
                numeric_pipeline.fit_transform(frame[numeric_columns]),
                columns=numeric_columns,
                index=frame.index,
            )
        else:
            numeric_frame = pd.DataFrame(index=frame.index)

        if categorical_columns:
            categorical_matrix = categorical_pipeline.fit_transform(frame[categorical_columns])
            encoder = categorical_pipeline.named_steps["encoder"]
            categorical_feature_names = list(encoder.get_feature_names_out(categorical_columns))
            categorical_frame = pd.DataFrame(categorical_matrix, columns=categorical_feature_names, index=frame.index)
        else:
            categorical_frame = pd.DataFrame(index=frame.index)

        encoded_frame = pd.concat([numeric_frame, categorical_frame], axis=1)
        if encoded_frame.empty:
            encoded_frame = frame[candidate_columns].copy()

        if labels is not None and labels.nunique(dropna=True) >= 2:
            model = RandomForestClassifier(n_estimators=250, random_state=42, n_jobs=-1, class_weight="balanced")
            model.fit(encoded_frame, labels)
            importance = dict(zip(encoded_frame.columns, model.feature_importances_, strict=False))
            ranked = sorted(importance.items(), key=lambda item: (-item[1], item[0]))
            selected_names = [name for name, _ in ranked[: self.top_k or max(10, min(len(ranked), 50))]]
            selected_frame = encoded_frame[selected_names].copy()
            report = {
                "mode": "supervised",
                "candidate_columns": candidate_columns,
                "encoded_feature_count": int(encoded_frame.shape[1]),
                "selected_feature_count": int(len(selected_names)),
            }
            feature_importance = summarize_top_features(importance)
        else:
            selector = VarianceThreshold(threshold=0.0)
            selected_matrix = selector.fit_transform(encoded_frame)
            support = selector.get_support()
            selected_names = encoded_frame.columns[support].tolist()
            selected_frame = pd.DataFrame(selected_matrix, columns=selected_names, index=frame.index)
            variances = dict(zip(encoded_frame.columns, selector.variances_, strict=False))
            report = {
                "mode": "unsupervised",
                "candidate_columns": candidate_columns,
                "encoded_feature_count": int(encoded_frame.shape[1]),
                "selected_feature_count": int(len(selected_names)),
            }
            feature_importance = summarize_top_features(variances)

        return FeatureSelectionArtifact(
            dataset_id=dataset_id,
            selected_feature_frame=selected_frame,
            selected_columns=selected_names,
            feature_importance=feature_importance,
            report=report,
            metadata={
                "numeric_columns": numeric_columns,
                "categorical_columns": categorical_columns,
                "encoded_feature_names": list(encoded_frame.columns),
            },
        )