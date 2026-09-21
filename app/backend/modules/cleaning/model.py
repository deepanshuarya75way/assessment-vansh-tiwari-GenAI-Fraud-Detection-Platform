from dataclasses import dataclass
from typing import Any

from sqlalchemy import ForeignKey, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.backend.common.mixins import TimestampMixin, UUIDPrimaryKeyMixin
from app.backend.db.base import Base


class CleanedData(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "cleaned_data"

    dataset_id: Mapped[str] = mapped_column(ForeignKey("datasets.id"), nullable=False, index=True)
    cleaned_parquet_path: Mapped[str] = mapped_column(Text, nullable=False)
    cleaning_summary: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    preprocessing_summary: Mapped[dict[str, Any] | None] = mapped_column(JSON)

    dataset = relationship("DatasetRecord", back_populates="cleaned_records")


@dataclass(slots=True)
class CleaningArtifact:
    rows_before: int
    rows_after: int
    duplicates_removed: int
    missing_filled: dict[str, int]
    date_columns_normalized: list[str]
    engineered_columns: list[str]
