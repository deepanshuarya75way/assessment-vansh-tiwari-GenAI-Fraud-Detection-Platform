from __future__ import annotations

import time
from collections import Counter

import numpy as np
import pandas as pd

from app.backend.agents.base import AgentContext, AgentLog, AgentResult, BaseAgent
from app.backend.agents.utils import build_time_buckets, top_counts


class AnalyticsAgent(BaseAgent):
    name = "analytics_agent"

    async def execute(self, context: AgentContext) -> AgentResult:
        started_at = time.time()
        logs = [AgentLog(level="INFO", message="Computing dataset analytics and fraud statistics.")]
        df: pd.DataFrame | None = context.artifacts.get("engineered_dataframe")
        fraud_results = context.artifacts.get("fraud_results", [])
        if df is None:
            raise ValueError("Analytics agent requires an engineered dataframe.")

        labels = [item["predicted_label"] for item in fraud_results]
        risk_scores = [float(item["risk_score"]) for item in fraud_results]
        fraud_count = labels.count("fraud")
        review_count = labels.count("review")
        safe_count = labels.count("safe")
        semantic_columns = context.artifacts.get("semantic_columns", {})

        payload = {
            "dataset_statistics": {
                "row_count": int(len(df)),
                "column_count": int(len(df.columns)),
                "columns": list(df.columns),
                "semantic_columns": semantic_columns,
                "missing_values": {column: int(count) for column, count in df.isna().sum().items() if count > 0},
                "duplicate_rows": int(df.duplicated().sum()),
            },
            "fraud_statistics": {
                "fraud_count": fraud_count,
                "review_count": review_count,
                "safe_count": safe_count,
                "fraud_percentage": round((fraud_count / max(len(labels), 1)) * 100, 2),
                "safe_percentage": round((safe_count / max(len(labels), 1)) * 100, 2),
                "high_risk_count": fraud_count,
                "medium_risk_count": review_count,
                "low_risk_count": safe_count,
                "average_risk_score": round(float(np.mean(risk_scores)) if risk_scores else 0.0, 2),
            },
            "trend_analysis": build_time_buckets(df, semantic_columns.get("date")),
            "category_analysis": top_counts(df[semantic_columns["category"]]) if semantic_columns.get("category") else [],
            "merchant_analysis": top_counts(df[semantic_columns["merchant"]]) if semantic_columns.get("merchant") else [],
            "location_analysis": top_counts(df[semantic_columns["location"]]) if semantic_columns.get("location") else [],
            "amount_analysis": self._amount_analysis(df, semantic_columns.get("amount")),
            "risk_analysis": self._risk_analysis(fraud_results),
            "insights": self._build_insights(fraud_results, df),
            "executive_statistics": {
                "total_analyzed": len(labels),
                "fraud_ratio": round((fraud_count / max(len(labels), 1)) * 100, 2),
            },
        }
        return self._build_result(
            status="success",
            summary="Analytics generated from uploaded dataset.",
            metadata={"dataset_id": context.dataset_id, "row_count": len(df)},
            payload=payload,
            logs=logs,
            started_at=started_at,
        )

    @staticmethod
    def _amount_analysis(df: pd.DataFrame, amount_column: str | None) -> dict[str, object]:
        if not amount_column or amount_column not in df.columns:
            return {}
        numeric = pd.to_numeric(df[amount_column], errors="coerce").dropna()
        if numeric.empty:
            return {}
        return {
            "min": float(numeric.min()),
            "max": float(numeric.max()),
            "mean": round(float(numeric.mean()), 2),
            "median": float(numeric.median()),
            "p95": float(numeric.quantile(0.95)),
        }

    @staticmethod
    def _risk_analysis(fraud_results: list[dict[str, object]]) -> dict[str, object]:
        scores = [float(item["risk_score"]) for item in fraud_results]
        if not scores:
            return {}
        buckets = Counter("high" if score >= 75 else "medium" if score >= 50 else "low" for score in scores)
        return {
            "risk_distribution": dict(buckets),
            "max_risk_score": max(scores),
            "min_risk_score": min(scores),
        }

    @staticmethod
    def _build_insights(fraud_results: list[dict[str, object]], df: pd.DataFrame) -> list[str]:
        insights = [f"Analyzed {len(df)} rows with {len(fraud_results)} fraud-scored records."]
        fraud_count = sum(1 for item in fraud_results if item["predicted_label"] == "fraud")
        if fraud_count:
            insights.append(f"Detected {fraud_count} high-risk transactions requiring review.")
        return insights