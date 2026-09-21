from dataclasses import dataclass


@dataclass(slots=True)
class FraudExplanation:
    row_identifier: str
    predicted_label: str
    risk_score: float
    explanation_text: str
    affected_features: list[str]
    explanation_payload: dict
