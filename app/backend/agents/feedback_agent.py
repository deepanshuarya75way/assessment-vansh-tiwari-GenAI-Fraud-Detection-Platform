from __future__ import annotations

import time

from app.backend.agents.base import AgentContext, AgentLog, AgentResult, BaseAgent


class FeedbackAgent(BaseAgent):
    name = "feedback_agent"

    async def execute(self, context: AgentContext) -> AgentResult:
        started_at = time.time()
        logs = [AgentLog(level="INFO", message="Aggregating analyst feedback for future learning.")]
        feedback_items = context.artifacts.get("feedback_items", [])
        retraining_rows = [item for item in feedback_items if item.get("corrected_label")]
        payload = {
            "dataset_id": context.dataset_id,
            "feedback_count": len(feedback_items),
            "labeled_examples": len(retraining_rows),
            "false_positives": sum(1 for item in feedback_items if item.get("corrected_label") == "safe"),
            "false_negatives": sum(1 for item in feedback_items if item.get("corrected_label") == "fraud"),
            "retraining_dataset": retraining_rows,
            "learning_metrics": {
                "correction_rate": round((len(retraining_rows) / max(len(feedback_items), 1)) * 100, 2),
            },
        }
        return self._build_result(
            status="success",
            summary="Feedback learning payload prepared without retraining the model.",
            metadata={"dataset_id": context.dataset_id},
            payload=payload,
            logs=logs,
            started_at=started_at,
        )