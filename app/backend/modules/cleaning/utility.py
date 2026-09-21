import pandas as pd


def clean_dataframe(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    rows_before = int(len(df))
    duplicates_removed = int(df.duplicated().sum())
    cleaned = df.drop_duplicates().copy()
    missing_filled: dict[str, int] = {}
    date_columns_normalized: list[str] = []

    for column in cleaned.columns:
        if pd.api.types.is_numeric_dtype(cleaned[column]):
            missing_count = int(cleaned[column].isna().sum())
            if missing_count:
                cleaned[column] = cleaned[column].fillna(cleaned[column].median())
                missing_filled[column] = missing_count
        elif pd.api.types.is_datetime64_any_dtype(cleaned[column]):
            missing_count = int(cleaned[column].isna().sum())
            if missing_count:
                cleaned[column] = cleaned[column].fillna(cleaned[column].mode().iloc[0] if not cleaned[column].mode().empty else cleaned[column].min())
                missing_filled[column] = missing_count
            date_columns_normalized.append(column)
        else:
            cleaned[column] = cleaned[column].astype("string").str.strip()
            missing_count = int(cleaned[column].isna().sum() + (cleaned[column] == "").sum())
            if missing_count:
                mode = cleaned[column].mode()
                fill_value = mode.iloc[0] if not mode.empty else "unknown"
                cleaned[column] = cleaned[column].replace("", pd.NA).fillna(fill_value)
                missing_filled[column] = missing_count

    engineered_columns: list[str] = []
    summary = {
        "rows_before": rows_before,
        "rows_after": int(len(cleaned)),
        "duplicates_removed": duplicates_removed,
        "missing_filled": missing_filled,
        "date_columns_normalized": date_columns_normalized,
        "engineered_columns": engineered_columns,
    }
    return cleaned, summary
