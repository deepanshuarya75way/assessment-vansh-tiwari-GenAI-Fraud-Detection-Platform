from __future__ import annotations

import time

from app.backend.agents.base import AgentContext, AgentLog, AgentResult, BaseAgent


class DashboardAgent(BaseAgent):
    name = "dashboard_agent"

    async def execute(self, context: AgentContext) -> AgentResult:
        started_at = time.time()
        logs = [AgentLog(level="INFO", message="Preparing dashboard payload from analytics output.")]
        analytics = context.artifacts.get("analytics")
        fraud_results = context.artifacts.get("fraud_results", [])
        if not analytics:
            raise ValueError("Dashboard agent requires analytics payload.")

        fraud_statistics = analytics["fraud_statistics"]
        payload = {
            "kpis": {
                "total_records": analytics["dataset_statistics"]["row_count"],
                "fraud_records": fraud_statistics["fraud_count"],
                "review_records": fraud_statistics["review_count"],
                "safe_records": fraud_statistics["safe_count"],
                "average_risk_score": fraud_statistics["average_risk_score"],
            },
            "charts": {
                "trend_analysis": analytics.get("trend_analysis", []),
                "category_analysis": analytics.get("category_analysis", []),
                "merchant_analysis": analytics.get("merchant_analysis", []),
                "location_analysis": analytics.get("location_analysis", []),
                "risk_analysis": analytics.get("risk_analysis", {}),
            },
            "tables": {
                "top_risk_transactions": fraud_results[:20],
            },
            "filters": {
                "available_columns": analytics["dataset_statistics"]["columns"],
                "semantic_columns": analytics["dataset_statistics"]["semantic_columns"],
            },
        }
        return self._build_result(
            status="success",
            summary="Dashboard payload prepared from dataset analytics.",
            metadata={"dataset_id": context.dataset_id},
            payload=payload,
            logs=logs,
            started_at=started_at,
        )