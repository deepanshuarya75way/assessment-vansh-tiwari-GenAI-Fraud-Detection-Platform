from app.backend.modules.uploads.model import DatasetPreview


def preview_from_dataframe(df) -> DatasetPreview:
    rows = df.head(5).replace({float("nan"): None}).to_dict(orient="records")
    return DatasetPreview(rows=rows, columns=list(df.columns))
