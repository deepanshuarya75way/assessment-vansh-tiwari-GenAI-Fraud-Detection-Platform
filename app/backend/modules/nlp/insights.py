from __future__ import annotations

from typing import Any


class InsightGenerator:
    def generate(self, summary: dict[str, Any]) -> list[str]:
        insights: list[str] = []
        fraud_distribution = summary.get("fraud_distribution", {})
        insights.append(f"The dataset contains {summary.get('row_count', 0)} rows and {summary.get('column_count', 0)} columns.")
        insights.append(
            f"Fraud summary: {fraud_distribution.get('fraud', 0)} fraud, {fraud_distribution.get('review', 0)} review, and {fraud_distribution.get('safe', 0)} safe records."
        )
        if summary.get("top_categories"):
            top_category = summary["top_categories"][0]
            insights.append(f"The most frequent transaction category is '{top_category['label']}' with {top_category['count']} records.")
        if summary.get("top_merchants"):
            top_merchant = summary["top_merchants"][0]
            insights.append(f"The most frequent merchant is '{top_merchant['label']}' with {top_merchant['count']} records.")
        if summary.get("amount_statistics"):
            insights.append(
                f"Transaction amounts range from {summary['amount_statistics'].get('min')} to {summary['amount_statistics'].get('max')}."
            )
        return insights