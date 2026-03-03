"""
Domain models and NLP pipeline classes for the Knowledge Management Agent.

Contains standalone classes that encapsulate embedding and entity-extraction
logic, kept separate from the agent itself so they can be tested and reused
independently.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from typing import Any

from agents.common.integration_services import LocalEmbeddingService

try:
    from sentence_transformers import SentenceTransformer
except ImportError:  # pragma: no cover - optional runtime dependency
    SentenceTransformer = None

try:
    import spacy
except ImportError:  # pragma: no cover - optional runtime dependency
    spacy = None


class SemanticEmbeddingService:
    """Embedding service backed by sentence-transformers with local fallback."""

    def __init__(
        self,
        model_name: str,
        fallback_service: LocalEmbeddingService,
        encoder: Any | None = None,
    ) -> None:
        self.model_name = model_name
        self.fallback_service = fallback_service
        self.encoder = encoder
        self.dimensions = fallback_service.dimensions

        if self.encoder is None and SentenceTransformer is not None:
            try:
                self.encoder = SentenceTransformer(model_name)
                dim_getter = getattr(self.encoder, "get_sentence_embedding_dimension", None)
                if callable(dim_getter):
                    self.dimensions = int(dim_getter())
            except (RuntimeError, ValueError, OSError) as exc:
                self.encoder = None
                self._load_error = str(exc)

    def embed(self, texts: list[str]) -> list[list[float]]:
        if self.encoder is None:
            return self.fallback_service.embed(texts)
        vectors = self.encoder.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
        return vectors.tolist()


class EntityExtractionPipeline:
    """Pluggable entity extraction with optional NLP backend and deterministic fallback."""

    PROJECT_ID_PATTERN = re.compile(r"\b(?:PRJ|PROJ|PROJECT)[-_]?[0-9]{2,6}\b", flags=re.IGNORECASE)
    DATE_PATTERN = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
    ORG_PATTERN = re.compile(
        r"\b([A-Z][A-Za-z0-9&.-]*(?:\s+[A-Z][A-Za-z0-9&.-]*)*\s+(?:Inc|LLC|Ltd|Corp|Corporation|Company|Group|Systems|Technologies))\b"
    )
    PERSON_PATTERN = re.compile(r"\b([A-Z][a-z]+\s+[A-Z][a-z]+)\b")

    def __init__(
        self,
        backend: str = "auto",
        custom_extractor: Callable[[str], list[dict[str, Any]]] | None = None,
    ):
        self.backend = backend
        self.custom_extractor = custom_extractor
        self._nlp_model = None
        self._nlp_available = False
        if backend in {"auto", "spacy"} and spacy is not None:
            try:
                self._nlp_model = spacy.load("en_core_web_sm")
                self._nlp_available = True
            except (OSError, ValueError):
                self._nlp_model = None

    def extract(self, text: str, limit: int = 20) -> list[dict[str, Any]]:
        if not text:
            return []

        entities: list[dict[str, Any]]
        if self.custom_extractor is not None:
            entities = self._normalize_entities(self.custom_extractor(text), text)
        elif self._nlp_available and self.backend != "fallback":
            entities = self._extract_with_spacy(text)
        else:
            entities = self._extract_with_fallback(text)

        entities.sort(key=lambda item: (item["position"], -item["score"], item["text"]))
        return entities[:limit]

    def _extract_with_spacy(self, text: str) -> list[dict[str, Any]]:
        doc = self._nlp_model(text)
        mapped = {"PERSON": "person", "ORG": "organization", "DATE": "date"}
        entities = []
        for ent in doc.ents:
            mapped_type = mapped.get(ent.label_)
            if not mapped_type:
                continue
            entities.append(
                {
                    "text": ent.text.strip(),
                    "type": mapped_type,
                    "score": 0.85,
                    "position": int(ent.start_char),
                    "span": {"start": int(ent.start_char), "end": int(ent.end_char)},
                }
            )

        # Ensure project IDs are included even when backend misses domain-specific formats.
        entities.extend(self._regex_entities(text, only_types={"project_id"}, score=0.92))
        return self._deduplicate(entities)

    def _extract_with_fallback(self, text: str) -> list[dict[str, Any]]:
        entities = self._regex_entities(text, score=0.78)
        return self._deduplicate(entities)

    def _regex_entities(
        self,
        text: str,
        *,
        only_types: set[str] | None = None,
        score: float,
    ) -> list[dict[str, Any]]:
        specs = [
            (
                self.PROJECT_ID_PATTERN,
                "project_id",
                lambda value: value.upper().replace("PROJECT", "PRJ"),
            ),
            (self.DATE_PATTERN, "date", lambda value: value),
            (self.ORG_PATTERN, "organization", lambda value: value),
            (self.PERSON_PATTERN, "person", lambda value: value),
        ]
        entities: list[dict[str, Any]] = []
        for pattern, ent_type, normalizer in specs:
            if only_types and ent_type not in only_types:
                continue
            for match in pattern.finditer(text):
                extracted = match.group(1) if match.lastindex else match.group(0)
                normalized_text = normalizer(extracted.strip())
                entities.append(
                    {
                        "text": normalized_text,
                        "type": ent_type,
                        "score": score,
                        "position": int(match.start()),
                        "span": {"start": int(match.start()), "end": int(match.end())},
                    }
                )
        return entities

    def _normalize_entities(
        self, entities: list[dict[str, Any]], text: str
    ) -> list[dict[str, Any]]:
        normalized = []
        for entity in entities:
            raw_text = str(entity.get("text", "")).strip()
            if not raw_text:
                continue
            start = entity.get("position")
            span = entity.get("span") if isinstance(entity.get("span"), dict) else {}
            start = int(span.get("start", start if isinstance(start, int) else text.find(raw_text)))
            end = int(span.get("end", max(start + len(raw_text), start)))
            normalized.append(
                {
                    "text": raw_text,
                    "type": str(entity.get("type", "entity")).lower(),
                    "score": float(entity.get("score", entity.get("confidence", 0.5))),
                    "position": start,
                    "span": {"start": start, "end": end},
                }
            )
        return self._deduplicate(normalized)

    def _deduplicate(self, entities: list[dict[str, Any]]) -> list[dict[str, Any]]:
        best: dict[tuple[str, str, int, int], dict[str, Any]] = {}
        for entity in entities:
            span = entity.get("span", {})
            key = (
                entity.get("text", "").strip(),
                entity.get("type", "entity"),
                int(span.get("start", entity.get("position", 0))),
                int(span.get("end", entity.get("position", 0))),
            )
            existing = best.get(key)
            if existing is None or entity.get("score", 0.0) > existing.get("score", 0.0):
                best[key] = entity
        return list(best.values())
