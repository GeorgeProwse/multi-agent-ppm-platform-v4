"""Agent annotation model and in-memory store for collaborative editing sessions."""

from __future__ import annotations

import time
import uuid
from typing import Any

from pydantic import BaseModel, Field


class Annotation(BaseModel):
    """An AI agent annotation attached to a canvas block within a coedit session."""

    annotation_id: str = Field(default_factory=lambda: f"ann-{uuid.uuid4().hex[:8]}")
    session_id: str = ""
    agent_id: str = ""
    agent_name: str = ""
    block_id: str = ""
    content: str = ""
    annotation_type: str = "suggestion"  # suggestion, warning, insight, quality
    created_at: float = Field(default_factory=time.time)
    dismissed: bool = False
    applied: bool = False


class AnnotationStore:
    """In-memory annotation store keyed by session_id."""

    def __init__(self) -> None:
        self._store: dict[str, list[Annotation]] = {}

    def create_annotation(self, session_id: str, annotation: Annotation) -> Annotation:
        annotation.session_id = session_id
        self._store.setdefault(session_id, []).append(annotation)
        return annotation

    def list_annotations(self, session_id: str, active_only: bool = True) -> list[Annotation]:
        annotations = self._store.get(session_id, [])
        if active_only:
            return [a for a in annotations if not a.dismissed]
        return list(annotations)

    def dismiss_annotation(self, annotation_id: str) -> Annotation | None:
        for annotations in self._store.values():
            for ann in annotations:
                if ann.annotation_id == annotation_id:
                    ann.dismissed = True
                    return ann
        return None

    def apply_annotation(self, annotation_id: str) -> Annotation | None:
        for annotations in self._store.values():
            for ann in annotations:
                if ann.annotation_id == annotation_id:
                    ann.applied = True
                    return ann
        return None


_annotation_store = AnnotationStore()


def get_annotation_store() -> AnnotationStore:
    return _annotation_store
