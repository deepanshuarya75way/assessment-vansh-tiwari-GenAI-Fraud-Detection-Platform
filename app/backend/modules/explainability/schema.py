from pydantic import BaseModel


class ExplainabilityResponse(BaseModel):
    row_identifier: str
    predicted_label: str
    risk_score: float
    explanation_text: str
    affected_features: list[str]
    explanation_payload: dict
