from __future__ import annotations

from app.backend.modules.nlp.artifacts import DatasetContextBundle, RetrievalHit


class PromptBuilder:
    def build(self, question: str, context: DatasetContextBundle, hits: list[RetrievalHit]) -> dict[str, str]:
        context_block = "\n".join(f"- [{hit.section}] {hit.text}" for hit in hits) if hits else "- No relevant dataset context was retrieved."
        system_prompt = (
            "You are a dataset-grounded fraud analysis assistant. Answer only from the provided uploaded dataset context. "
            "If the data is missing, unavailable, or unsupported, say so clearly. Never use external knowledge."
        )
        user_prompt = (
            f"Dataset ID: {context.dataset_id}\n"
            f"Question: {question}\n"
            f"Dataset summary: {context.summary}\n"
            f"Retrieved context:\n{context_block}\n"
            "Return a concise, structured answer with references to retrieved sections when possible."
        )
        return {"system": system_prompt, "user": user_prompt, "context": context_block}