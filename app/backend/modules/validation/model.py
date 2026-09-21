from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class ValidationArtifact:
    row_count: int
    column_count: int
    duplicate_rows: int
    missing_by_column: dict[str, int]
    outlier_columns: dict[str, int]
    semantic_columns: dict[str, str | None]
    dtypes: dict[str, str]
    warnings: list[str]
    issues: list[str]
    preview_columns: list[str]
    metadata: dict[str, Any]
