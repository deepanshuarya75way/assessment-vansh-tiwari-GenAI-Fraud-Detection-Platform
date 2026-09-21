from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class AnalyticsArtifact:
    project_id: str
    payload: dict[str, Any]
