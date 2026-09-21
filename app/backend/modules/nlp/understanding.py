from __future__ import annotations

from collections import Counter
from typing import Any

import pandas as pd

from app.backend.modules.nlp.artifacts import ContextDocument
from app.backend.modules.ml.utils import threshold_summary


class DatasetUnderstandingEngine:
    def summarize(
        self,
        dataset_id: str,
        frame: pd.DataFrame,
        semantic_columns: dict[str, str | None],
        fraud_results: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        fraud_results = fraud_results or []
        labels = [item.get("predicted_label") for item in fraud_results]
        risk_scores = [float(item.get("risk_score", 0.0)) for item in fraud_results]
        amount_column = semantic_columns.get("amount")
        amount_stats = self._amount_stats(frame, amount_column)

        summary = {
            "dataset_id": dataset_id,
            "row_count": int(len(frame)),
            "column_count": int(len(frame.columns)),
            "columns": list(frame.columns),
            "semantic_columns": semantic_columns,
            "dtypes": {column: str(dtype) for column, dtype in frame.dtypes.items()},
            "missing_values": {column: int(count) for column, count in frame.isna().sum().items() if count > 0},
            "duplicate_rows": int(frame.duplicated().sum()),
            "fraud_distribution": {
                "fraud": labels.count("fraud"),
                "review": labels.count("review"),
                "safe": labels.count("safe"),
            },
            "risk_thresholds": threshold_summary(risk_scores) if risk_scores else {},
            "top_categories": self._top_values(frame, semantic_columns.get("category")),
            "top_merchants": self._top_values(frame, semantic_columns.get("merchant")),
            "top_locations": self._top_values(frame, semantic_columns.get("location")),
            "amount_statistics": amount_stats,
        }
        return summary

    def build_documents(self, dataset_id: str, summary: dict[str, Any], sample_rows: list[dict[str, Any]] | None = None) -> list[ContextDocument]:
        documents: list[ContextDocument] = [
            ContextDocument(
                document_id=f"{dataset_id}:summary",
                text=(
                    f"Dataset {dataset_id} contains {summary.get('row_count', 0)} rows and {summary.get('column_count', 0)} columns. "
                    f"Fraud distribution: {summary.get('fraud_distribution', {})}."
                ),
                source="dataset_summary",
                section="summary",
                metadata={"dataset_id": dataset_id},
            )
        ]
        if sample_rows:
            for index, row in enumerate(sample_rows[:20]):
                documents.append(
                    ContextDocument(
                        document_id=f"{dataset_id}:row:{index}",
                        text="; ".join(f"{key}: {value}" for key, value in row.items()),
                        source="sample_row",
                        section="rows",
                        metadata={"dataset_id": dataset_id, "row_index": index},
                    )
                )
        return documents

    @staticmethod
    def _top_values(frame: pd.DataFrame, column: str | None, limit: int = 5) -> list[dict[str, Any]]:
        if not column or column not in frame.columns:
            return []
        counts = Counter(frame[column].fillna("unknown").astype(str))
        return [{"label": label, "count": count} for label, count in counts.most_common(limit)]

    @staticmethod
    def _amount_stats(frame: pd.DataFrame, amount_column: str | None) -> dict[str, Any]:
        if not amount_column or amount_column not in frame.columns:
            return {}
        numeric = pd.to_numeric(frame[amount_column], errors="coerce").dropna()
        if numeric.empty:
            return {}
        return {
            "min": float(numeric.min()),
            "max": float(numeric.max()),
            "mean": round(float(numeric.mean()), 2),
            "median": float(numeric.median()),
            "p95": float(numeric.quantile(0.95)),
        }