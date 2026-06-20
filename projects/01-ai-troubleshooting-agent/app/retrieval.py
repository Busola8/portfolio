from __future__ import annotations

import json
import logging
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any

from .settings import Settings


TOKEN_RE = re.compile(r"[a-z0-9_]+")
logger = logging.getLogger("troubleshooting-agent.retrieval")


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


class KnowledgeRetriever:
    """RAG retriever with local TF-IDF fallback and optional OpenAI embeddings."""

    def __init__(self, knowledge_path: Path, settings: Settings | None = None) -> None:
        self.knowledge_path = knowledge_path
        self.settings = settings
        self.documents = self._load_documents()
        self.document_tokens = [
            tokenize(f"{doc['title']} {doc['service']} {doc['symptoms']} {doc['content']}")
            for doc in self.documents
        ]
        self.idf = self._compute_idf(self.document_tokens)
        self.document_vectors = [self._vectorize(tokens) for tokens in self.document_tokens]
        self.embedding_client = None
        self.embedding_vectors: list[list[float]] = []
        if settings and settings.openai_enabled:
            try:
                self._initialize_openai_embeddings(settings)
            except Exception as exc:
                logger.warning("OpenAI embeddings unavailable; using local retrieval: %s", exc)
                self.embedding_client = None
                self.embedding_vectors = []

    def _load_documents(self) -> list[dict[str, Any]]:
        with self.knowledge_path.open(encoding="utf-8") as file:
            data = json.load(file)
        return data["articles"]

    @staticmethod
    def _compute_idf(corpus: list[list[str]]) -> dict[str, float]:
        document_count = len(corpus)
        frequencies: Counter[str] = Counter()
        for tokens in corpus:
            frequencies.update(set(tokens))
        return {
            token: math.log((1 + document_count) / (1 + count)) + 1
            for token, count in frequencies.items()
        }

    def _vectorize(self, tokens: list[str]) -> dict[str, float]:
        counts = Counter(tokens)
        return {token: count * self.idf.get(token, 1.0) for token, count in counts.items()}

    @staticmethod
    def _cosine(left: dict[str, float], right: dict[str, float]) -> float:
        shared = set(left) & set(right)
        numerator = sum(left[token] * right[token] for token in shared)
        left_norm = math.sqrt(sum(value * value for value in left.values()))
        right_norm = math.sqrt(sum(value * value for value in right.values()))
        if not left_norm or not right_norm:
            return 0.0
        return numerator / (left_norm * right_norm)

    def search(self, query: str, limit: int = 3) -> list[dict[str, Any]]:
        if self.embedding_client and self.embedding_vectors:
            return self._embedding_search(query, limit)
        query_vector = self._vectorize(tokenize(query))
        scored = []
        for doc, doc_vector in zip(self.documents, self.document_vectors):
            score = self._cosine(query_vector, doc_vector)
            scored.append({**doc, "score": round(score, 3)})
        return sorted(scored, key=lambda item: item["score"], reverse=True)[:limit]

    def _initialize_openai_embeddings(self, settings: Settings) -> None:
        from openai import OpenAI

        self.embedding_client = OpenAI(api_key=settings.openai_api_key)
        inputs = [
            f"{doc['title']} {doc['service']} {doc['symptoms']} {doc['content']}"
            for doc in self.documents
        ]
        response = self.embedding_client.embeddings.create(
            model=settings.embedding_model,
            input=inputs,
        )
        self.embedding_vectors = [item.embedding for item in response.data]

    @staticmethod
    def _dense_cosine(left: list[float], right: list[float]) -> float:
        numerator = sum(left_value * right_value for left_value, right_value in zip(left, right))
        left_norm = math.sqrt(sum(value * value for value in left))
        right_norm = math.sqrt(sum(value * value for value in right))
        if not left_norm or not right_norm:
            return 0.0
        return numerator / (left_norm * right_norm)

    def _embedding_search(self, query: str, limit: int) -> list[dict[str, Any]]:
        assert self.embedding_client is not None
        assert self.settings is not None
        response = self.embedding_client.embeddings.create(
            model=self.settings.embedding_model,
            input=query,
        )
        query_vector = response.data[0].embedding
        scored = []
        for doc, doc_vector in zip(self.documents, self.embedding_vectors):
            score = self._dense_cosine(query_vector, doc_vector)
            scored.append({**doc, "score": round(score, 3), "retrieval_backend": "openai"})
        return sorted(scored, key=lambda item: item["score"], reverse=True)[:limit]
