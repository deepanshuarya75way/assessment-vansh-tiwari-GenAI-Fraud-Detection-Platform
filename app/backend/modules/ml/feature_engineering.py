from __future__ import annotations

from typing import Any

import pandas as pd

from app.backend.modules.ml.artifacts import FeatureEngineeringArtifact
from app.backend.utils.dataframe import coerce_datetime_columns, coerce_numeric_candidates, infer_semantic_columns, normalize_columns
from app.backend.utils.dataframe import frequency_scores, robust_z_scores


class FeatureEngineeringEngine:
    def __init__(self, *, preserve_columns: list[str] | None = None) -> None:
        self.preserve_columns = preserve_columns or []

    def transform(
        self,
        dataset_id: str,
        frame: pd.DataFrame,
        semantic_columns: dict[str, str | None] | None = None,
    ) -> FeatureEngineeringArtifact:
        working = normalize_columns(frame.copy())
        working = coerce_numeric_candidates(working)
        inferred = semantic_columns or infer_semantic_columns(working)
        working = coerce_datetime_columns(working, inferred)

        engineered_columns: list[str] = []
        removed_columns: list[str] = []

        for column in list(working.columns):
            if column in self.preserve_columns:
                continue
            if working[column].nunique(dropna=True) <= 1:
                removed_columns.append(column)
                working = working.drop(columns=[column])

        date_column = inferred.get("date")
        if date_column and date_column in working.columns and pd.api.types.is_datetime64_any_dtype(working[date_column]):
            working[f"{date_column}_hour"] = working[date_column].dt.hour.fillna(-1)
            working[f"{date_column}_dayofweek"] = working[date_column].dt.dayofweek.fillna(-1)
            working[f"{date_column}_month"] = working[date_column].dt.month.fillna(-1)
            engineered_columns.extend([f"{date_column}_hour", f"{date_column}_dayofweek", f"{date_column}_month"])

        amount_column = inferred.get("amount")
        if amount_column and amount_column in working.columns and pd.api.types.is_numeric_dtype(working[amount_column]):
            working[f"{amount_column}_log"] = pd.Series(working[amount_column]).fillna(0).abs().map(lambda value: value + 1).map(lambda value: value if value > 0 else 1)
            working[f"{amount_column}_zscore"] = robust_z_scores(working[amount_column]).fillna(0.0)
            engineered_columns.extend([f"{amount_column}_log", f"{amount_column}_zscore"])

        for semantic_key in ("merchant", "category", "account", "location"):
            column = inferred.get(semantic_key)
            if column and column in working.columns:
                rarity_column = f"{column}_rarity"
                working[rarity_column] = frequency_scores(working[column])
                engineered_columns.append(rarity_column)

        report = {
            "input_columns": list(frame.columns),
            "output_columns": list(working.columns),
            "semantic_columns": inferred,
            "engineered_columns": engineered_columns,
            "removed_columns": removed_columns,
            "row_count": int(len(working)),
            "column_count": int(len(working.columns)),
        }
        return FeatureEngineeringArtifact(
            dataset_id=dataset_id,
            feature_frame=working,
            engineered_columns=engineered_columns,
            removed_columns=removed_columns,
            report=report,
            metadata={"semantic_columns": inferred},
        )