from __future__ import annotations

from typing import Any

from app.backend.modules.chatbot.context import ChatSessionContext
from app.backend.modules.nlp.context_builder import DatasetContextBuilder
from app.backend.modules.nlp.response_engine import DatasetResponseEngine


class ChatResponseGenerator:
    def __init__(self, response_engine: DatasetResponseEngine | None = None) -> None:
        self.response_engine = response_engine or DatasetResponseEngine()

    def generate(self, context: ChatSessionContext, question: str) -> dict[str, Any]:
        if context.data_frame is None or context.dataset_id is None:
            return {
                "answer": "The uploaded dataset does not contain this information.",
                "summary": "The chatbot can only answer from the active analysis session.",
                "important_findings": [],
                "evidence": [],
                "recommendations": ["Upload and process a dataset before asking questions."],
                "next_suggested_questions": ["Generate Summary", "Explain Dashboard", "Show High Risk Transactions"],
                "visual_response": {"type": "message"},
                "confidence": 0.0,
                "prompt": {"system": "", "user": "", "context": ""},
            }

        semantic_columns = {}
        if context.validation_report:
            semantic_columns = context.validation_report.get("semantic_columns", {}) or {}

        dataset_context = DatasetContextBuilder().build(
            context.dataset_id,
            context.data_frame,
            semantic_columns,
            fraud_results=[
                {
                    "predicted_label": item.predicted_label,
                    "risk_score": item.risk_score,
                    "row_identifier": item.row_identifier,
                }
                for item in context.detection_results
            ],
            project_id=context.project_id,
            sample_rows=context.data_frame.head(20).replace({None: None}).to_dict(orient="records"),
        )
        response = self.response_engine.answer(question, dataset_context, allowed_sections=["summary", "rows"])
        evidence = [
            {"document_id": hit.document_id, "section": hit.section, "score": hit.score, "source": hit.source}
            for hit in response.references
        ]
        visual_response = self._visual_response(context.intent, context)
        return {
            "answer": response.answer,
            "summary": response.summary.get("executive_summary", ""),
            "important_findings": response.summary.get("insights", [])[:4],
            "evidence": evidence,
            "recommendations": response.summary.get("recommendations", []),
            "next_suggested_questions": self._next_questions(context.intent, context),
            "visual_response": visual_response,
            "confidence": response.confidence,
            "prompt": response.prompt,
            "retrieved_context": response.summary,
            "metadata": response.metadata,
        }

    def _visual_response(self, intent: str, context: ChatSessionContext) -> dict[str, Any]:
        if intent in {"fraud_count", "high_risk_only", "highest_risk_transaction"}:
            return {"type": "table", "dataset_ref": context.dataset_id, "filter": {"predicted_label": ["fraud", "review"]}}
        if intent in {"dashboard_explain", "risk_analysis"}:
            return {"type": "dashboard_cards", "dataset_ref": context.dataset_id}
        if intent == "report_explain":
            return {"type": "report", "dataset_ref": context.dataset_id}
        if intent == "time_analysis":
            return {"type": "chart", "chart": "timeline", "dataset_ref": context.dataset_id}
        return {"type": "message", "dataset_ref": context.dataset_id}

    def _next_questions(self, intent: str, context: ChatSessionContext) -> list[str]:
        if intent == "fraud_count":
            return ["Show High Risk Transactions", "Highest Risk Merchant", "Explain Dashboard", "Generate Report"]
        if intent == "dashboard_explain":
            return ["Explain Fraud Distribution", "Generate Summary", "Business Insights", "Generate Report"]
        if intent == "report_explain":
            return ["Explain Recommendations", "Business Insights", "Show High Risk Transactions", "Generate Executive Summary"]
        if context.detection_results:
            return ["Show Fraud Table", "Generate Summary", "Explain Dashboard", "Highest Risk Transaction"]
        return ["Generate Summary", "Explain Dashboard", "Business Insights", "Generate Report"]