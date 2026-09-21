from pydantic import BaseModel

from app.backend.common.schemas import TimestampedResponse


class UploadResponse(TimestampedResponse):
    project_id: str
    original_filename: str
    stored_path: str
    file_type: str
    checksum: str
    size_bytes: int
    row_count: int | None
    column_count: int | None
    upload_status: str


class DatasetResponse(TimestampedResponse):
    project_id: str
    source_upload_ids: list[str]
    raw_parquet_path: str
    schema_profile: dict
    row_count: int
    label_column: str | None
    date_column: str | None
    amount_column: str | None
    category_column: str | None
    merchant_column: str | None
    location_column: str | None


class DatasetPreviewResponse(BaseModel):
    columns: list[str]
    rows: list[dict]
