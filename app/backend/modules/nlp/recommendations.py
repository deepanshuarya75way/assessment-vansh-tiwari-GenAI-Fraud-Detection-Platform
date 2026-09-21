from __future__ import annotations

from typing import Any


class RecommendationEngine:
    def generate(self, summary: dict[str, Any]) -> list[str]:
        recommendations: list[str] = []
        fraud_distribution = summary.get("fraud_distribution", {})
        if fraud_distribution.get("fraud", 0) > 0:
            recommendations.append("Prioritize manual review for transactions classified as fraud risk high.")
        if summary.get("top_merchants"):
            recommendations.append(
                f"Monitor merchant '{summary['top_merchants'][0]['label']}' for unusual concentration or repeated risky transactions."
            )
        if summary.get("top_locations"):
            recommendations.append(
                f"Increase controls in location '{summary['top_locations'][0]['label']}' if it remains concentrated in suspicious activity."
            )
        if summary.get("missing_values"):
            recommendations.append("Improve data completeness to strengthen detection and downstream explanation quality.")
        recommendations.append("Use validated analyst feedback to create future retraining datasets without automatically changing the model.")
        return recommendations