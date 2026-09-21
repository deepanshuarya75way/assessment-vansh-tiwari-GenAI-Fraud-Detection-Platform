from __future__ import annotations

from collections.abc import Iterable


def classify_question(question: str) -> str:
    normalized = question.lower().strip()
    if any(term in normalized for term in ("how many fraud", "fraud count", "fraud transactions", "total fraud")):
        return "fraud_count"
    if any(term in normalized for term in ("highest risk", "top risk", "most risky", "max risk")):
        return "highest_risk"
    if any(term in normalized for term in ("review count", "how many review", "manual review")):
        return "review_count"
    if any(term in normalized for term in ("safe count", "how many safe", "non fraud")):
        return "safe_count"
    if "dashboard" in normalized:
        return "dashboard_summary"
    return "dataset_summary"


def summarize_top_values(values: Iterable[str], limit: int = 3) -> list[dict[str, int | str]]:
    counts: dict[str, int] = {}
    for value in values:
        text = str(value)
        counts[text] = counts.get(text, 0) + 1
    ordered = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return [{"label": label, "count": count} for label, count in ordered[:limit]]