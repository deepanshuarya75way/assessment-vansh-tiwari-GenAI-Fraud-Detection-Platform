from typing import Any

import numpy as np
import pandas as pd

from app.backend.utils.dataframe import robust_z_scores


def detect_numeric_outliers(df: pd.DataFrame) -> dict[str, int]:
    outliers: dict[str, int] = {}
    numeric_df = df.select_dtypes(include=[np.number])
    for column in numeric_df.columns:
        scores = robust_z_scores(numeric_df[column]).abs()
        count = int((scores > 3.5).sum())
        if count > 0:
            outliers[column] = count
    return outliers


def validation_messages(profile: dict[str, Any], outliers: dict[str, int]) -> tuple[list[str], list[str]]:
    warnings: list[str] = []
    issues: list[str] = []

    if profile["row_count"] == 0:
        issues.append("The uploaded dataset is empty.")
    if profile["duplicate_rows"] > 0:
        warnings.append(f"{profile['duplicate_rows']} duplicate rows were detected.")
    if profile["missing_by_column"]:
        warnings.append("Missing values were detected and should be cleaned before detection.")
    if outliers:
        warnings.append("Potential numeric outliers were detected based on robust z-scores.")
    if not profile["semantic_columns"].get("amount"):
        issues.append("No amount-like column could be inferred from the uploaded dataset.")
    return warnings, issues
