from __future__ import annotations

import asyncio
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any, Iterable

from app.backend.agents.base import AgentContext, AgentResult, BaseAgent
from app.backend.agents.state import OrchestratorState


class AIOrchestrator:
    def __init__(self, agents: Iterable[BaseAgent]) -> None:
        self.agents = list(agents)

    async def run(self, context: AgentContext) -> OrchestratorState:
        state = OrchestratorState(dataset_id=context.dataset_id, project_id=context.project_id)
        total_agents = max(len(self.agents), 1)

        for index, agent in enumerate(self.agents, start=1):
            state.current_stage = agent.name
            state.logs.append({
                "level": "INFO",
                "message": f"Starting {agent.name}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            try:
                result = await self._execute_agent(agent, context)
                state.results[agent.name] = self._serialize_result(result)
                state.completed_stages.append(agent.name)
                state.progress = round((index / total_agents) * 100)
                state.progress_messages.append({
                    "stage": agent.name,
                    "status": result.status,
                    "summary": result.summary,
                    "progress": state.progress,
                })
            except Exception as exc:  # pragma: no cover - orchestration safety net
                state.status = "failed"
                state.failed_stage = agent.name
                state.logs.append({
                    "level": "ERROR",
                    "message": f"{agent.name} failed",
                    "error": str(exc),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
                break

        if state.status != "failed":
            state.status = "completed"
            state.current_stage = None
            state.progress = 100
            state.finished_at = datetime.now(timezone.utc).isoformat()

        return state

    async def _execute_agent(self, agent: BaseAgent, context: AgentContext) -> AgentResult:
        return await agent.execute(context)

    @staticmethod
    def _serialize_result(result: AgentResult) -> dict[str, Any]:
        return {
            "agent_name": result.agent_name,
            "status": result.status,
            "summary": result.summary,
            "metadata": result.metadata,
            "processing_time_seconds": result.processing_time_seconds,
            "logs": [asdict(log) for log in result.logs],
            "result_location": result.result_location,
            "payload": result.payload,
            "warnings": result.warnings,
            "errors": result.errors,
        }