from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


try:  # pragma: no cover - optional dependency
    from sentence_transformers import SentenceTransformer
except Exception:  # pragma: no cover - optional dependency
    SentenceTransformer = None


@dataclass(slots=True)
class EmbeddingResult:
    texts: list[str]
    vectors: np.ndarray
    backend: str


class EmbeddingEngine:
    def __init__(self, *, backend: str = "tfidf", model_name: str | None = None) -> None:
        self.backend = backend
        self.model_name = model_name
        self._tfidf: TfidfVectorizer | None = None
        self._sentence_model = None

    def fit(self, texts: list[str]) -> EmbeddingResult:
        if self.backend == "sentence_transformers" and SentenceTransformer is not None:
            model_name = self.model_name or "all-MiniLM-L6-v2"
            self._sentence_model = SentenceTransformer(model_name)
            vectors = np.asarray(self._sentence_model.encode(texts, normalize_embeddings=True))
            return EmbeddingResult(texts=texts, vectors=vectors, backend="sentence_transformers")

        self._tfidf = TfidfVectorizer(stop_words="english", max_features=5000)
        vectors = self._tfidf.fit_transform(texts).toarray()
        return EmbeddingResult(texts=texts, vectors=vectors, backend="tfidf")

    def encode(self, texts: list[str]) -> np.ndarray:
        if self._sentence_model is not None:
            return np.asarray(self._sentence_model.encode(texts, normalize_embeddings=True))
        if self._tfidf is None:
            raise ValueError("EmbeddingEngine must be fitted before encoding text.")
        return self._tfidf.transform(texts).toarray()

    def similarity(self, query: str, documents: list[str]) -> list[float]:
        if not documents:
            return []
        all_texts = [query, *documents]
        result = self.fit(all_texts)
        query_vector = result.vectors[0:1]
        doc_vectors = result.vectors[1:]
        scores = cosine_similarity(query_vector, doc_vectors)[0]
        return [float(score) for score in scores]