from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(slots=True)
class OrchestratorState:
    dataset_id: str
    project_id: str | None = None
    status: str = "pending"
    current_stage: str | None = None
    completed_stages: list[str] = field(default_factory=list)
    failed_stage: str | None = None
    progress: int = 0
    progress_messages: list[dict[str, Any]] = field(default_factory=list)
    logs: list[dict[str, Any]] = field(default_factory=list)
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    finished_at: str | None = None
    results: dict[str, Any] = field(default_factory=dict)
