from app.backend.core.exceptions import ProcessingError


def ensure_feature_columns(columns: list[str]) -> None:
    if not columns:
        raise ProcessingError("No usable feature columns were derived from the uploaded dataset.")
