"""
Risk Management Agent - Service and extractor models.

Contains CognitiveSearchService, KnowledgeBaseQueryService, and RiskNLPExtractor
which are used by the RiskManagementAgent for risk identification and extraction.
"""

import importlib.util
import json
import re
from typing import Any
from urllib import error as url_error
from urllib import request as url_request


class CognitiveSearchService:
    """Lightweight Azure Cognitive Search helper for risk extraction."""

    def __init__(
        self,
        endpoint: str | None,
        api_key: str | None,
        index_name: str | None,
        api_version: str = "2023-11-01",
    ) -> None:
        self.endpoint = endpoint
        self.api_key = api_key
        self.index_name = index_name
        self.api_version = api_version

    def is_configured(self) -> bool:
        return bool(self.endpoint and self.api_key and self.index_name)

    def search(
        self, query: str, *, top: int = 5, filter_expression: str | None = None
    ) -> list[dict[str, Any]]:
        if not self.is_configured():
            return []
        url = (
            f"{self.endpoint}/indexes/{self.index_name}/docs/search?api-version={self.api_version}"
        )
        payload: dict[str, Any] = {"search": query, "top": top}
        if filter_expression:
            payload["filter"] = filter_expression
        data = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key or "",
        }
        req = url_request.Request(url, data=data, headers=headers, method="POST")
        try:
            with url_request.urlopen(req) as response:
                body = response.read().decode("utf-8")
                parsed = json.loads(body)
                return parsed.get("value", [])
        except (url_error.URLError, json.JSONDecodeError, ValueError):
            return []

    def extract_risks(self, documents: list[dict[str, Any] | str]) -> list[dict[str, Any]]:
        extracted: list[dict[str, Any]] = []
        if not documents:
            return extracted
        if self.is_configured():
            queries = []
            for document in documents:
                if isinstance(document, dict):
                    queries.append(
                        str(
                            document.get("title")
                            or document.get("query")
                            or document.get("content")
                            or ""
                        )
                    )
                else:
                    queries.append(str(document))
            for query in [q.strip() for q in queries if q.strip()]:
                results = self.search(f"{query} risk", top=3)
                for result in results:
                    title = result.get("title") or result.get("id") or "Risk signal"
                    description = result.get("content") or result.get("description") or str(result)
                    extracted.append(
                        {
                            "title": title,
                            "description": description,
                            "category": "document",
                            "source": result.get("source") or "cognitive_search",
                        }
                    )
            if extracted:
                return extracted
        for document in documents:
            text = document.get("content") if isinstance(document, dict) else str(document)
            for line in str(text).splitlines():
                if "risk" in line.lower():
                    extracted.append(
                        {
                            "title": line.strip()[:80] or "Document risk",
                            "description": line.strip(),
                            "category": "document",
                            "source": "heuristic",
                        }
                    )
        return extracted


class KnowledgeBaseQueryService:
    """Query SharePoint/Confluence for mitigation guidance."""

    def __init__(
        self,
        document_service: Any,
        documentation_service: Any,
    ) -> None:
        self.document_service = document_service
        self.documentation_service = documentation_service

    async def query_mitigations(self, risk: dict[str, Any]) -> list[dict[str, Any]]:
        query = f"{risk.get('category', '')} mitigation {risk.get('title', '')}".strip()
        results: list[dict[str, Any]] = []

        confluence_connector = self.documentation_service._get_confluence_connector()
        if confluence_connector and hasattr(confluence_connector, "read"):
            try:
                pages = confluence_connector.read(
                    "pages",
                    filters={"query": query},
                    limit=5,
                )
                for page in pages or []:
                    results.append(
                        {
                            "title": page.get("title"),
                            "strategy": page.get("excerpt") or page.get("title"),
                            "source": "confluence",
                        }
                    )
            except (
                ConnectionError,
                TimeoutError,
                ValueError,
                KeyError,
                TypeError,
                RuntimeError,
                OSError,
            ):
                results = results

        sharepoint_connector = self.document_service._get_connector()
        if sharepoint_connector and hasattr(sharepoint_connector, "read"):
            try:
                documents = sharepoint_connector.read(
                    "documents",
                    filters={"search": query},
                    limit=5,
                )
                for document in documents or []:
                    results.append(
                        {
                            "title": document.get("Title") or document.get("title"),
                            "strategy": document.get("Description") or document.get("summary"),
                            "source": "sharepoint",
                        }
                    )
            except (
                ConnectionError,
                TimeoutError,
                ValueError,
                KeyError,
                TypeError,
                RuntimeError,
                OSError,
            ):
                results = results

        return [item for item in results if item.get("strategy")]


class RiskNLPExtractor:
    """Extract risks from text using a transformer model with fallback heuristics."""

    def __init__(
        self,
        *,
        model_name: str = "bert-base-uncased",
        pipeline_task: str = "zero-shot-classification",
        labels: list[str] | None = None,
        threshold: float = 0.6,
        max_sentences: int = 80,
        training_keywords: tuple[str, ...] | None = None,
    ) -> None:
        self.model_name = model_name
        self.pipeline_task = pipeline_task
        self.labels = labels or ["risk", "no risk"]
        self.threshold = threshold
        self.max_sentences = max_sentences
        self.training_keywords = training_keywords or (
            "risk",
            "delay",
            "overrun",
            "issue",
            "compliance",
            "shortage",
            "failure",
            "defect",
            "breach",
        )
        self._pipeline = None
        self._sklearn_model = None
        self._vectorizer = None
        self._trained = False

    def is_available(self) -> bool:
        return importlib.util.find_spec("transformers") is not None

    def is_sklearn_available(self) -> bool:
        return importlib.util.find_spec("sklearn") is not None

    def train(self, documents: list[dict[str, Any] | str]) -> bool:
        sentences = self._collect_sentences(documents)
        if not sentences or not self.is_sklearn_available():
            return False

        labeled: list[tuple[str, int]] = []
        for sentence in sentences:
            label = 1 if self._is_risk_sentence(sentence) else 0
            labeled.append((sentence, label))

        if len(labeled) < 4:
            return False
        if len({label for _, label in labeled}) < 2:
            return False

        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.linear_model import LogisticRegression

            texts = [text for text, _ in labeled]
            labels = [label for _, label in labeled]
            vectorizer = TfidfVectorizer(stop_words="english")
            features = vectorizer.fit_transform(texts)
            model = LogisticRegression(max_iter=200)
            model.fit(features, labels)
            self._vectorizer = vectorizer
            self._sklearn_model = model
            self._trained = True
            return True
        except (
            ConnectionError,
            TimeoutError,
            ValueError,
            KeyError,
            TypeError,
            RuntimeError,
            OSError,
        ):
            self._sklearn_model = None
            self._vectorizer = None
            self._trained = False
            return False

    def extract_risks(self, documents: list[dict[str, Any] | str]) -> list[dict[str, Any]]:
        sentences = self._collect_sentences(documents)
        if not sentences:
            return []
        if self._trained and self._sklearn_model and self._vectorizer:
            return self._sklearn_risks(sentences)
        self._ensure_pipeline()
        if self._pipeline is None:
            return self._heuristic_risks(sentences)
        return self._model_risks(sentences)

    def _ensure_pipeline(self) -> None:
        if self._pipeline is not None or not self.is_available():
            return
        from transformers import pipeline

        try:
            self._pipeline = pipeline(self.pipeline_task, model=self.model_name)
        except (
            ConnectionError,
            TimeoutError,
            ValueError,
            KeyError,
            TypeError,
            RuntimeError,
            OSError,
        ):
            self._pipeline = None

    def _collect_sentences(self, documents: list[dict[str, Any] | str]) -> list[str]:
        sentences: list[str] = []
        for document in documents:
            if isinstance(document, dict):
                text = str(document.get("content") or document.get("text") or document)
            else:
                text = str(document)
            for sentence in re.split(r"(?<=[.!?])\s+", text):
                cleaned = sentence.strip()
                if cleaned:
                    sentences.append(cleaned)
            if len(sentences) >= self.max_sentences:
                break
        return sentences[: self.max_sentences]

    def _heuristic_risks(self, sentences: list[str]) -> list[dict[str, Any]]:
        extracted: list[dict[str, Any]] = []
        for sentence in sentences:
            if self._is_risk_sentence(sentence):
                extracted.append(
                    {
                        "title": sentence[:80],
                        "description": sentence,
                        "category": "nlp",
                        "source": "heuristic_nlp",
                    }
                )
        return extracted

    def _sklearn_risks(self, sentences: list[str]) -> list[dict[str, Any]]:
        extracted: list[dict[str, Any]] = []
        if not self._trained or not self._sklearn_model or not self._vectorizer:
            return extracted
        try:
            features = self._vectorizer.transform(sentences)
            probabilities = self._sklearn_model.predict_proba(features)[:, 1]
        except (
            ConnectionError,
            TimeoutError,
            ValueError,
            KeyError,
            TypeError,
            RuntimeError,
            OSError,
        ):
            return self._heuristic_risks(sentences)
        for sentence, probability in zip(sentences, probabilities):
            if probability >= self.threshold:
                extracted.append(
                    {
                        "title": sentence[:80],
                        "description": sentence,
                        "category": "nlp",
                        "source": "sklearn",
                        "confidence": float(round(probability, 4)),
                    }
                )
        return extracted

    def _model_risks(self, sentences: list[str]) -> list[dict[str, Any]]:
        extracted: list[dict[str, Any]] = []
        for sentence in sentences:
            if self.pipeline_task == "zero-shot-classification":
                result = self._pipeline(sentence, self.labels)
                scores = dict(zip(result.get("labels", []), result.get("scores", [])))
                risk_score = scores.get(self.labels[0], 0.0)
                if risk_score >= self.threshold:
                    extracted.append(
                        {
                            "title": sentence[:80],
                            "description": sentence,
                            "category": "nlp",
                            "source": "transformer",
                            "confidence": risk_score,
                        }
                    )
            else:
                result = self._pipeline(sentence)
                if isinstance(result, list):
                    result = result[0] if result else {}
                label = str(result.get("label", "")).lower()
                score = float(result.get("score", 0.0))
                if "risk" in label or score >= self.threshold:
                    extracted.append(
                        {
                            "title": sentence[:80],
                            "description": sentence,
                            "category": "nlp",
                            "source": "transformer",
                            "confidence": score,
                        }
                    )
        return extracted

    def _is_risk_sentence(self, sentence: str) -> bool:
        lowered = sentence.lower()
        return any(keyword in lowered for keyword in self.training_keywords)
