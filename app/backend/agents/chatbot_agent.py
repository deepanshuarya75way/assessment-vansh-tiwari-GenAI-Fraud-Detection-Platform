from __future__ import annotations

import time

from app.backend.agents.base import AgentContext, AgentLog, AgentResult, BaseAgent


class ChatbotAgent(BaseAgent):
    name = "chatbot_agent"

    async def execute(self, context: AgentContext) -> AgentResult:
        started_at = time.time()
        logs = [AgentLog(level="INFO", message="Answering dataset-grounded user question.")]
        question = str(context.input_data.get("question") or "").strip()
        analytics = context.artifacts.get("analytics", {})
        fraud_results = context.artifacts.get("fraud_results", [])
        if not question:
            raise ValueError("Chatbot agent requires a question.")

        lower = question.lower()
        fraud_count = analytics.get("fraud_statistics", {}).get("fraud_count", 0)
        review_count = analytics.get("fraud_statistics", {}).get("review_count", 0)
        safe_count = analytics.get("fraud_statistics", {}).get("safe_count", 0)

        if "how many fraud" in lower:
            answer = f"The uploaded dataset contains {fraud_count} fraud transactions."
        elif "highest risk" in lower:
            top = max(fraud_results, key=lambda item: item.get("risk_score", 0), default=None)
            answer = (
                f"The highest-risk record is row {top['row_identifier']} with risk score {top['risk_score']:.2f}."
                if top
                else "No risky records were found in the uploaded dataset."
            )
        elif "dashboard" in lower:
            answer = (
                f"Dashboard summary: {fraud_count} fraud, {review_count} review, and {safe_count} safe transactions."
            )
        else:
            answer = (
                f"I can answer questions grounded in the uploaded dataset. Current summary: {fraud_count} fraud, "
                f"{review_count} review, and {safe_count} safe records."
            )

        payload = {
            "dataset_id": context.dataset_id,
            "question": question,
            "answer": answer,
            "references": {
                "fraud_count": fraud_count,
                "review_count": review_count,
                "safe_count": safe_count,
            },
            "dataset_context": {
                "available_sections": ["analytics", "dashboard", "fraud_results"],
            },
        }
        return self._build_result(
            status="success",
            summary="Dataset-grounded chatbot answer generated.",
            metadata={"dataset_id": context.dataset_id},
            payload=payload,
            logs=logs,
            started_at=started_at,
        )