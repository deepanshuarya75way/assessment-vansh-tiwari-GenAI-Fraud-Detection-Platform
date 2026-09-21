from __future__ import annotations

from typing import Any

from app.backend.modules.nlp.artifacts import ContextDocument, RetrievalHit
from app.backend.modules.nlp.embeddings import EmbeddingEngine


class RetrievalEngine:
    def __init__(self, embedding_engine: EmbeddingEngine | None = None) -> None:
        self.embedding_engine = embedding_engine or EmbeddingEngine()

    def retrieve(
        self,
        query: str,
        documents: list[ContextDocument],
        top_k: int = 5,
        allowed_sections: list[str] | None = None,
    ) -> list[RetrievalHit]:
        filtered = [document for document in documents if not allowed_sections or document.section in allowed_sections]
        if not filtered:
            return []
        similarities = self.embedding_engine.similarity(query, [document.text for document in filtered])
        ranked = sorted(zip(filtered, similarities, strict=False), key=lambda item: (-item[1], item[0].document_id))
        return [
            RetrievalHit(
                document_id=document.document_id,
                score=float(score),
                text=document.text,
                section=document.section,
                source=document.source,
                metadata=document.metadata,
            )
            for document, score in ranked[:top_k]
        ]