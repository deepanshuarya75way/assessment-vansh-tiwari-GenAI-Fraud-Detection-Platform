from __future__ import annotations

from typing import Any


class SummaryGenerator:
    def generate_executive_summary(self, summary: dict[str, Any]) -> str:
        fraud_distribution = summary.get("fraud_distribution", {})
        return (
            f"The uploaded dataset contains {summary.get('row_count', 0)} records across {summary.get('column_count', 0)} columns. "
            f"Fraud analysis identified {fraud_distribution.get('fraud', 0)} fraud records, "
            f"{fraud_distribution.get('review', 0)} review records, and {fraud_distribution.get('safe', 0)} safe records."
        )

    def generate_technical_summary(self, summary: dict[str, Any]) -> str:
        semantic_columns = summary.get("semantic_columns", {})
        amount_column = semantic_columns.get("amount")
        date_column = semantic_columns.get("date")
        return (
            f"The dataset schema was interpreted dynamically. Amount column: {amount_column or 'unavailable'}. "
            f"Date column: {date_column or 'unavailable'}. Missing values, duplicates, and risk thresholds were derived from the uploaded file."
        )