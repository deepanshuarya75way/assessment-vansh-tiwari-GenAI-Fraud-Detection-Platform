from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class DetectionArtifact:
    project_id: str
    dataset_id: str
    strategy: str
    metrics: dict[str, Any]
    thresholds: dict[str, float]
    total_records: int
    fraud_count: int
    review_count: int
    safe_count: int
