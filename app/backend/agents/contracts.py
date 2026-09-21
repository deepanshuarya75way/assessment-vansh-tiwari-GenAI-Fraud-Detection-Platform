from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class DatasetArtifact:
    dataset_id: str
    project_id: str | None
    raw_path: str
    cleaned_path: str | None = None
    engineered_path: str | None = None
    schema_profile: dict[str, Any] | None = None
    validation_report: dict[str, Any] | None = None
    cleaning_report: dict[str, Any] | None = None
    preprocessing_summary: dict[str, Any] | None = None
