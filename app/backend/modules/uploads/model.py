from dataclasses import dataclass
from typing import Any

from sqlalchemy import ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.backend.common.mixins import TimestampMixin, UUIDPrimaryKeyMixin
from app.backend.db.base import Base
from app.backend.db.enterprise_models import UploadRecord  # Import from enterprise models


class DatasetRecord(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "datasets"

    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), index=True, nullable=False)
    source_upload_ids: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    raw_parquet_path: Mapped[str] = mapped_column(Text, nullable=False)
    schema_profile: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    row_count: Mapped[int] = mapped_column(nullable=False)
    label_column: Mapped[str | None] = mapped_column(String(255))
    date_column: Mapped[str | None] = mapped_column(String(255))
    amount_column: Mapped[str | None] = mapped_column(String(255))
    category_column: Mapped[str | None] = mapped_column(String(255))
    merchant_column: Mapped[str | None] = mapped_column(String(255))
    location_column: Mapped[str | None] = mapped_column(String(255))

    project = relationship("Project", back_populates="datasets")
    cleaned_records = relationship("CleanedData", back_populates="dataset")
    fraud_results = relationship("FraudResult", back_populates="dataset")


@dataclass(slots=True)
class DatasetPreview:
    rows: list[dict[str, Any]]
    columns: list[str]
