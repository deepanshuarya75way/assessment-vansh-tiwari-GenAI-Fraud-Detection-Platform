from __future__ import annotations

import numpy as np
import pandas as pd

from app.backend.utils.dataframe import frequency_scores, robust_z_scores


def engineer_features(df: pd.DataFrame, semantic_columns: dict[str, str | None]) -> tuple[pd.DataFrame, list[str]]:
    engineered = df.copy()
    new_columns: list[str] = []

    date_column = semantic_columns.get("date")
    if date_column and date_column in engineered.columns and pd.api.types.is_datetime64_any_dtype(engineered[date_column]):
        engineered[f"{date_column}_hour"] = engineered[date_column].dt.hour.fillna(-1)
        engineered[f"{date_column}_dayofweek"] = engineered[date_column].dt.dayofweek.fillna(-1)
        engineered[f"{date_column}_month"] = engineered[date_column].dt.month.fillna(-1)
        new_columns.extend(
            [
                f"{date_column}_hour",
                f"{date_column}_dayofweek",
                f"{date_column}_month",
            ]
        )

    amount_column = semantic_columns.get("amount")
    if amount_column and amount_column in engineered.columns and pd.api.types.is_numeric_dtype(engineered[amount_column]):
        engineered[f"{amount_column}_log"] = np.log1p(np.abs(engineered[amount_column].fillna(0)))
        engineered[f"{amount_column}_zscore"] = robust_z_scores(engineered[amount_column]).fillna(0.0)
        new_columns.extend([f"{amount_column}_log", f"{amount_column}_zscore"])

    for semantic_key in ("merchant", "category", "account", "location"):
        column = semantic_columns.get(semantic_key)
        if column and column in engineered.columns:
            feature_name = f"{column}_rarity"
            engineered[feature_name] = frequency_scores(engineered[column])
            new_columns.append(feature_name)

    return engineered, new_columns


def select_feature_columns(df: pd.DataFrame, semantic_columns: dict[str, str | None]) -> tuple[list[str], list[str], list[str]]:
    excluded = {value for key, value in semantic_columns.items() if key in {"label", "transaction_id"} and value}
    numeric_columns = [
        column
        for column in df.select_dtypes(include=[np.number]).columns
        if column not in excluded
    ]
    categorical_columns: list[str] = []
    for column in df.select_dtypes(include=["object", "string", "category"]).columns:
        if column in excluded:
            continue
        unique_ratio = df[column].nunique(dropna=True) / max(len(df), 1)
        if df[column].nunique(dropna=True) <= 100 or unique_ratio <= 0.25:
            categorical_columns.append(column)

    feature_columns = numeric_columns + categorical_columns
    return feature_columns, numeric_columns, categorical_columns


def normalize_label_series(series: pd.Series) -> pd.Series | None:
    mapping = {
        "1": 1,
        "true": 1,
        "yes": 1,
        "fraud": 1,
        "fraudulent": 1,
        "0": 0,
        "false": 0,
        "no": 0,
        "safe": 0,
        "legit": 0,
        "legitimate": 0,
    }
    normalized = series.dropna().astype(str).str.strip().str.lower().map(mapping)
    if normalized.empty or normalized.isna().all():
        return None
    full = series.astype(str).str.strip().str.lower().map(mapping)
    if full.nunique(dropna=True) < 2:
        return None
    return full.astype("float").fillna(0).astype(int)
