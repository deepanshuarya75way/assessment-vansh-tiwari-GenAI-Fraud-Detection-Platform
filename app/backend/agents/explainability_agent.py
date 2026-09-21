from __future__ import annotations

import time
from collections import Counter

from app.backend.agents.base import AgentContext, AgentLog, AgentResult, BaseAgent


class ExplainabilityAgent(BaseAgent):
    name = "explainability_agent"

    async def execute(self, context: AgentContext) -> AgentResult:
        started_at = time.time()
        logs = [AgentLog(level="INFO", message="Generating human-readable transaction explanations.")]
        fraud_results = context.artifacts.get("fraud_results", [])
        if not fraud_results:
            return self._build_result(
                status="warning",
                summary="No fraud records were available for explainability generation.",
                metadata={"dataset_id": context.dataset_id},
                payload={"dataset_id": context.dataset_id, "explanations": []},
                logs=logs,
                started_at=started_at,
                warnings=["Fraud detection output was empty."],
            )

        explanations: list[dict[str, object]] = []
        for item in fraud_results:
            if item["predicted_label"] == "safe":
                continue
            risk_score = float(item["risk_score"])
            if risk_score >= 80:
                reason = "Transaction marked High Risk because the score and feature pattern were strongly anomalous."
            elif risk_score >= 60:
                reason = "Transaction marked Medium Risk because transaction behavior deviated from the dataset baseline."
            else:
                reason = "Transaction marked for review because it showed unusual but not extreme behavior."
            explanations.append(
                {
                    "row_identifier": item["row_identifier"],
                    "reason": reason,
                    "confidence": item["confidence_score"],
                    "risk_factors": [
                        "Large amount",
                        "Unusual category",
                        "High-risk pattern",
                    ],
                    "important_features": list(item.get("feature_snapshot", {}).keys())[:5],
                    "risk_score": risk_score,
                }
            )

        feature_counter = Counter(feature for row in explanations for feature in row["important_features"])
        payload = {
            "dataset_id": context.dataset_id,
            "explanations": explanations,
            "feature_importance": [{"feature": key, "count": value} for key, value in feature_counter.most_common()],
        }
        return self._build_result(
            status="success",
            summary="Explainability records generated for suspicious transactions.",
            metadata={"dataset_id": context.dataset_id, "explanation_count": len(explanations)},
            payload=payload,
            logs=logs,
            started_at=started_at,
        )