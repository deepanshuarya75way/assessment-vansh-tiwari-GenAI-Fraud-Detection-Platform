from app.backend.common.schemas import TimestampedResponse


class CleanedDataResponse(TimestampedResponse):
    dataset_id: str
    cleaned_parquet_path: str
    cleaning_summary: dict
    preprocessing_summary: dict | None
