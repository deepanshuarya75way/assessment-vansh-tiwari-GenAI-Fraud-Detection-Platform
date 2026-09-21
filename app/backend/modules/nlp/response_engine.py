from __future__ import annotations

from typing import Any

from app.backend.modules.nlp.artifacts import DatasetContextBundle, NLPResponseArtifact
from app.backend.modules.nlp.insights import InsightGenerator
from app.backend.modules.nlp.prompt_builder import PromptBuilder
from app.backend.modules.nlp.recommendations import RecommendationEngine
from app.backend.modules.nlp.retrieval import RetrievalEngine
from app.backend.modules.nlp.summary import SummaryGenerator


class DatasetResponseEngine:
    def __init__(
        self,
        retrieval_engine: RetrievalEngine | None = None,
        prompt_builder: PromptBuilder | None = None,
        summary_generator: SummaryGenerator | None = None,
        insight_generator: InsightGenerator | None = None,
        recommendation_engine: RecommendationEngine | None = None,
    ) -> None:
        self.retrieval_engine = retrieval_engine or RetrievalEngine()
        self.prompt_builder = prompt_builder or PromptBuilder()
        self.summary_generator = summary_generator or SummaryGenerator()
        self.insight_generator = insight_generator or InsightGenerator()
        self.recommendation_engine = recommendation_engine or RecommendationEngine()

    def answer(
        self,
        question: str,
        context: DatasetContextBundle,
        *,
        top_k: int = 5,
        allowed_sections: list[str] | None = None,
    ) -> NLPResponseArtifact:
        hits = self.retrieval_engine.retrieve(question, context.documents, top_k=top_k, allowed_sections=allowed_sections)
        prompt = self.prompt_builder.build(question, context, hits)
        answer = self._generate_answer(question, context, hits)
        confidence = self._confidence_score(hits, context)
        summary = {
            "executive_summary": self.summary_generator.generate_executive_summary(context.summary),
            "technical_summary": self.summary_generator.generate_technical_summary(context.summary),
            "insights": self.insight_generator.generate(context.summary),
            "recommendations": self.recommendation_engine.generate(context.summary),
        }
        return NLPResponseArtifact(
            dataset_id=context.dataset_id,
            question=question,
            answer=answer,
            confidence=confidence,
            references=hits,
            prompt=prompt["user"],
            summary=summary,
            metadata={"context_document_count": len(context.documents), "retrieved_hits": len(hits)},
        )

    def _generate_answer(self, question: str, context: DatasetContextBundle, hits: list[Any]) -> str:
        lower = question.lower().strip()
        fraud_distribution = context.summary.get("fraud_distribution", {})

        if not context.documents:
            return "No uploaded dataset context is available for this question."

        if any(term in lower for term in ("how many fraud", "fraud transactions", "fraud count")):
            return f"The uploaded dataset contains {fraud_distribution.get('fraud', 0)} fraud transactions."
        if any(term in lower for term in ("highest fraud amount", "highest amount", "largest transaction")):
            amount_stats = context.summary.get("amount_statistics", {})
            if not amount_stats:
                return "The dataset does not provide an interpretable amount column for this question."
            return f"The maximum observed transaction amount is {amount_stats.get('max')}."
        if any(term in lower for term in ("most risky merchant", "highest risk merchant", "merchant")) and context.summary.get("top_merchants"):
            merchant = context.summary["top_merchants"][0]
            return f"The most frequent merchant in the uploaded dataset is '{merchant['label']}' with {merchant['count']} records."
        if any(term in lower for term in ("show top fraud categories", "fraud category", "category")) and context.summary.get("top_categories"):
            category = context.summary["top_categories"][0]
            return f"The most frequent category in the uploaded dataset is '{category['label']}' with {category['count']} records."
        if "explain dashboard" in lower or "explain report" in lower or "summarize uploaded data" in lower:
            return self.summary_generator.generate_executive_summary(context.summary)
        if not hits:
            return "The question cannot be answered from the currently retrieved dataset context."
        joined = "; ".join(hit.text for hit in hits[:3])
        return f"Based on the uploaded dataset context, the most relevant information is: {joined}."

    @staticmethod
    def _confidence_score(hits: list[Any], context: DatasetContextBundle) -> float:
        if not hits:
            return 0.25
        top_score = max(float(hit.score) for hit in hits)
        coverage = min(len(hits) / max(len(context.documents), 1), 1.0)
        score = 0.5 * top_score + 0.5 * coverage
        return round(max(min(score, 1.0), 0.0), 4)