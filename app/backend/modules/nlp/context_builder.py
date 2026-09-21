from __future__ import annotations

from typing import Any

import pandas as pd

from app.backend.modules.nlp.artifacts import DatasetContextBundle
from app.backend.modules.nlp.understanding import DatasetUnderstandingEngine


class DatasetContextBuilder:
    def __init__(self, understanding_engine: DatasetUnderstandingEngine | None = None) -> None:
        self.understanding_engine = understanding_engine or DatasetUnderstandingEngine()

    def build(
        self,
        dataset_id: str,
        frame: pd.DataFrame,
        semantic_columns: dict[str, str | None],
        fraud_results: list[dict[str, Any]] | None = None,
        project_id: str | None = None,
        sample_rows: list[dict[str, Any]] | None = None,
    ) -> DatasetContextBundle:
        summary = self.understanding_engine.summarize(dataset_id, frame, semantic_columns, fraud_results)
        documents = self.understanding_engine.build_documents(
            dataset_id,
            summary,
            sample_rows or frame.head(20).replace({pd.NA: None}).to_dict(orient="records"),
        )
        return DatasetContextBundle(
            dataset_id=dataset_id,
            project_id=project_id,
            documents=documents,
            summary=summary,
            metadata={
                "semantic_columns": semantic_columns,
                "document_count": len(documents),
            },
        )