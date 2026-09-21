from __future__ import annotations

import time

from app.backend.agents.base import AgentContext, AgentLog, AgentResult, BaseAgent


class ReportAgent(BaseAgent):
    name = "report_agent"

    async def execute(self, context: AgentContext) -> AgentResult:
        started_at = time.time()
        logs = [AgentLog(level="INFO", message="Generating enterprise report JSON.")]
        analytics = context.artifacts.get("analytics")
        dashboard = context.artifacts.get("dashboard")
        explainability = context.artifacts.get("explainability", {})
        if not analytics or not dashboard:
            raise ValueError("Report agent requires analytics and dashboard payloads.")

        payload = {
            "executive_summary": {
                "total_records": analytics["dataset_statistics"]["row_count"],
                "fraud_records": analytics["fraud_statistics"]["fraud_count"],
                "review_records": analytics["fraud_statistics"]["review_count"],
                "safe_records": analytics["fraud_statistics"]["safe_count"],
            },
            "technical_summary": {
                "strategy": context.artifacts.get("fraud_detection", {}).get("strategy", "dataset_risk_scoring"),
                "analytics_sections": list(analytics.keys()),
            },
            "fraud_summary": analytics["fraud_statistics"],
            "risk_summary": analytics.get("risk_analysis", {}),
            "charts_summary": dashboard["charts"],
            "ai_insights": analytics.get("insights", []),
            "explainability_summary": explainability.get("explanations", []),
            "recommendations": [
                "Review high-risk clusters identified in the dataset.",
                "Use analyst feedback to enrich future retraining datasets.",
                "Prioritize manual review for transactions above the fraud threshold.",
            ],
            "output_formats": ["pdf", "word", "excel"],
        }
        return self._build_result(
            status="success",
            summary="Report payload prepared for PDF/Word/Excel export.",
            metadata={"dataset_id": context.dataset_id},
            payload=payload,
            logs=logs,
            started_at=started_at,
        )