from __future__ import annotations

from app.backend.modules.nlp.prompt_builder import PromptBuilder


class ChatPromptEngine:
    def __init__(self, prompt_builder: PromptBuilder | None = None) -> None:
        self.prompt_builder = prompt_builder or PromptBuilder()

    def build(self, question: str, context) -> dict[str, str]:
        hits = []
        for item in getattr(context, "detection_results", [])[:5]:
            hits.append(
                type(
                    "Hit",
                    (),
                    {
                        "section": "fraud_results",
                        "text": f"row {item.row_identifier} -> {item.predicted_label} risk {item.risk_score}",
                    },
                )()
            )
        return self.prompt_builder.build(question, context, hits)