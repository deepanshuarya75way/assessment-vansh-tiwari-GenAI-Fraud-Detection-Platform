from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ContextDocument:
    document_id: str
    text: str
    source: str
    section: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class DatasetContextBundle:
    dataset_id: str
    project_id: str | None
    documents: list[ContextDocument]
    summary: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class RetrievalHit:
    document_id: str
    score: float
    text: str
    section: str
    source: str
    metadata: dict[str, Any]


@dataclass(slots=True)
class NLPResponseArtifact:
    dataset_id: str
    question: str
    answer: str
    confidence: float
    references: list[RetrievalHit]
    prompt: str
    summary: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    errors: list[dict[str, Any]] = field(default_factory=list)