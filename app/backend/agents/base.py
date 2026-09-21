from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class AgentContext:
    dataset_id: str
    project_id: str | None = None
    input_data: dict[str, Any] = field(default_factory=dict)
    configuration: dict[str, Any] = field(default_factory=dict)
    execution_context: dict[str, Any] = field(default_factory=dict)
    artifacts: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class AgentLog:
    level: str
    message: str
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class AgentResult:
    agent_name: str
    status: str
    summary: str
    metadata: dict[str, Any]
    processing_time_seconds: float
    logs: list[AgentLog]
    result_location: str | None
    payload: dict[str, Any]
    warnings: list[str] = field(default_factory=list)
    errors: list[dict[str, Any]] = field(default_factory=list)


class BaseAgent(ABC):
    name: str

    @abstractmethod
    async def execute(self, context: AgentContext) -> AgentResult:
        raise NotImplementedError

    def _build_result(
        self,
        *,
        status: str,
        summary: str,
        metadata: dict[str, Any],
        payload: dict[str, Any],
        logs: list[AgentLog],
        started_at: float,
        result_location: str | None = None,
        warnings: list[str] | None = None,
        errors: list[dict[str, Any]] | None = None,
    ) -> AgentResult:
        return AgentResult(
            agent_name=self.name,
            status=status,
            summary=summary,
            metadata=metadata,
            processing_time_seconds=round(time.time() - started_at, 4),
            logs=logs,
            result_location=result_location,
            payload=payload,
            warnings=warnings or [],
            errors=errors or [],
        )