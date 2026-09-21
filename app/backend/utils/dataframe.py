from __future__ import annotations

import math
import re
from collections import Counter
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

SEMANTIC_COLUMN_HINTS = {
    "label": ("label", "fraud", "target", "class", "is_fraud", "isfraud", "flagged", "status"),
    "date": ("date", "time", "timestamp", "created", "posted", "transaction_date"),
    "amount": ("amount", "amt", "value", "transaction_amount", "payment"),
    "category": ("category", "type", "segment", "transaction_type"),
    "merchant": ("merchant", "vendor", "seller", "beneficiary", "counterparty"),
    "location": ("city", "state", "country", "region", "location"),
    "account": ("account", "customer", "client", "card", "iban", "wallet"),
    "transaction_id": ("transaction_id", "txn_id", "reference", "ref", "id"),
}


def normalize_column_name(name: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", name.strip().lower()).strip("_")
    return normalized or "column"


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    renamed = {column: normalize_column_name(str(column)) for column in df.columns}
    return df.rename(columns=renamed)


def load_dataframe(path: Path) -> pd.DataFrame:
    extension = path.suffix.lower()
    if extension == ".csv":
        try:
            return pd.read_csv(path, engine="pyarrow")
        except Exception:
            return pd.read_csv(path)
    if extension in {".xlsx", ".xls"}:
        return pd.read_excel(path, engine="openpyxl")
    raise ValueError(f"Unsupported file type: {path.suffix}")


def merge_dataframes(frames: Iterable[pd.DataFrame]) -> pd.DataFrame:
    normalized_frames = [normalize_columns(frame.copy()) for frame in frames]
    if not normalized_frames:
        raise ValueError("No dataframes were provided for merging.")
    return pd.concat(normalized_frames, ignore_index=True, sort=False)


def infer_semantic_columns(df: pd.DataFrame) -> dict[str, str | None]:
    semantic_map: dict[str, str | None] = {key: None for key in SEMANTIC_COLUMN_HINTS}
    lower_columns = {column.lower(): column for column in df.columns}

    for semantic_key, hints in SEMANTIC_COLUMN_HINTS.items():
        for hint in hints:
            for lowered, original in lower_columns.items():
                if hint == lowered or hint in lowered:
                    semantic_map[semantic_key] = original
                    break
            if semantic_map[semantic_key]:
                break

    if not semantic_map["date"]:
        for column in df.columns:
            series = df[column]
            if series.dtype == "datetime64[ns]":
                semantic_map["date"] = column
                break

    if not semantic_map["amount"]:
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        if numeric_columns:
            semantic_map["amount"] = max(numeric_columns, key=lambda column: df[column].abs().mean())

    if not semantic_map["transaction_id"]:
        object_columns = df.select_dtypes(include=["object", "string"]).columns.tolist()
        if object_columns:
            semantic_map["transaction_id"] = object_columns[0]

    return semantic_map


def coerce_datetime_columns(df: pd.DataFrame, semantic_columns: dict[str, str | None]) -> pd.DataFrame:
    date_column = semantic_columns.get("date")
    if date_column and date_column in df.columns:
        df[date_column] = pd.to_datetime(df[date_column], errors="coerce", utc=True)
    return df


def coerce_numeric_candidates(df: pd.DataFrame) -> pd.DataFrame:
    for column in df.columns:
        if df[column].dtype == "object":
            cleaned = (
                df[column]
                .astype(str)
                .str.replace(",", "", regex=False)
                .str.replace("$", "", regex=False)
                .str.strip()
            )
            numeric = pd.to_numeric(cleaned, errors="coerce")
            if numeric.notna().mean() >= 0.85:
                df[column] = numeric
    return df


def make_row_identifier(df: pd.DataFrame, semantic_columns: dict[str, str | None]) -> pd.Series:
    transaction_id_column = semantic_columns.get("transaction_id")
    if transaction_id_column and transaction_id_column in df.columns:
        return df[transaction_id_column].astype(str).fillna("").replace("", np.nan).fillna(df.index.astype(str))
    return df.index.astype(str)


def frequency_scores(series: pd.Series) -> pd.Series:
    counts = Counter(series.fillna("unknown").astype(str))
    total = max(len(series), 1)
    return series.fillna("unknown").astype(str).map(lambda value: -math.log((counts[value] + 1) / (total + len(counts))))


def robust_z_scores(series: pd.Series) -> pd.Series:
    clean = pd.to_numeric(series, errors="coerce")
    median = clean.median()
    mad = np.median(np.abs(clean.dropna() - median))
    if not mad or np.isnan(mad):
        std = clean.std(ddof=0) or 1.0
        return ((clean - clean.mean()) / std).fillna(0.0)
    return (0.6745 * (clean - median) / mad).fillna(0.0)


def dataframe_profile(df: pd.DataFrame) -> dict[str, Any]:
    semantic_columns = infer_semantic_columns(df)
    duplicate_count = int(df.duplicated().sum())
    missing_by_column = {column: int(count) for column, count in df.isna().sum().items() if count > 0}
    dtypes = {column: str(dtype) for column, dtype in df.dtypes.items()}
    numeric_summary = (
        df.select_dtypes(include=[np.number]).describe().replace({np.nan: None}).to_dict()
        if not df.select_dtypes(include=[np.number]).empty
        else {}
    )
    return {
        "row_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "columns": list(df.columns),
        "semantic_columns": semantic_columns,
        "duplicate_rows": duplicate_count,
        "missing_by_column": missing_by_column,
        "dtypes": dtypes,
        "numeric_summary": numeric_summary,
    }
