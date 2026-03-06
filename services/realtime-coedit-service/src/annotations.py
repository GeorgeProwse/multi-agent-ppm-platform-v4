"""Agent annotation model and store for collaborative editing sessions.

Supports file-backed persistence and LLM-powered annotation suggestions.
"""

from __future__ import annotations

import json
import logging
import os
import time
import uuid
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger("coedit.annotations")

# Persistence directory
_STORAGE_DIR = Path(os.getenv("ANNOTATION_STORAGE_DIR", "/tmp/ppm-annotations"))


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
    """Annotation store with file-backed persistence."""

    def __init__(self, persist: bool = True) -> None:
        self._store: dict[str, list[Annotation]] = {}
        self._persist = persist
        self._loaded_sessions: set[str] = set()

    def _storage_path(self, session_id: str) -> Path:
        return _STORAGE_DIR / f"{session_id}.json"

    def _load_session(self, session_id: str) -> None:
        """Load annotations for a session from disk if not already loaded."""
        if session_id in self._loaded_sessions:
            return
        self._loaded_sessions.add(session_id)

        if not self._persist:
            return

        path = self._storage_path(session_id)
        if path.exists():
            try:
                with open(path) as f:
                    data = json.load(f)
                annotations = [Annotation.model_validate(a) for a in data if isinstance(a, dict)]
                self._store[session_id] = annotations
            except Exception as exc:
                logger.debug("Failed to load annotations for %s: %s", session_id, exc)

    def _save_session(self, session_id: str) -> None:
        """Persist annotations for a session to disk."""
        if not self._persist:
            return
        try:
            _STORAGE_DIR.mkdir(parents=True, exist_ok=True)
            path = self._storage_path(session_id)
            annotations = self._store.get(session_id, [])
            with open(path, "w") as f:
                json.dump([a.model_dump() for a in annotations], f, indent=2)
        except Exception as exc:
            logger.debug("Failed to save annotations for %s: %s", session_id, exc)

    def create_annotation(self, session_id: str, annotation: Annotation) -> Annotation:
        self._load_session(session_id)
        annotation.session_id = session_id
        self._store.setdefault(session_id, []).append(annotation)
        self._save_session(session_id)
        return annotation

    def list_annotations(self, session_id: str, active_only: bool = True) -> list[Annotation]:
        self._load_session(session_id)
        annotations = self._store.get(session_id, [])
        if active_only:
            return [a for a in annotations if not a.dismissed]
        return list(annotations)

    def dismiss_annotation(self, annotation_id: str) -> Annotation | None:
        for session_id, annotations in self._store.items():
            for ann in annotations:
                if ann.annotation_id == annotation_id:
                    ann.dismissed = True
                    self._save_session(session_id)
                    return ann
        return None

    def apply_annotation(self, annotation_id: str) -> Annotation | None:
        for session_id, annotations in self._store.items():
            for ann in annotations:
                if ann.annotation_id == annotation_id:
                    ann.applied = True
                    self._save_session(session_id)
                    return ann
        return None


_annotation_store = AnnotationStore()


def get_annotation_store() -> AnnotationStore:
    return _annotation_store


# ---------------------------------------------------------------------------
# LLM-powered annotation suggestions
# ---------------------------------------------------------------------------

async def generate_suggestions(
    session_id: str,
    block_id: str,
    block_content: str,
    context: dict[str, Any] | None = None,
) -> list[Annotation]:
    """Generate AI-powered annotation suggestions for a block.

    Uses LLM when available, falls back to rule-based analysis.
    """
    suggestions: list[Annotation] = []

    # Try LLM-powered suggestions
    try:
        llm_result = await _llm_suggest(block_content, context or {})
        if isinstance(llm_result, list):
            for item in llm_result:
                if isinstance(item, dict) and item.get("content"):
                    ann = Annotation(
                        session_id=session_id,
                        agent_id=item.get("agent_id", "quality-management"),
                        agent_name=item.get("agent_name", "Quality Agent"),
                        block_id=block_id,
                        content=item["content"],
                        annotation_type=item.get("type", "suggestion"),
                    )
                    suggestions.append(ann)
            if suggestions:
                return suggestions
    except Exception as exc:
        logger.debug("LLM suggestion failed: %s", exc)

    # Fallback: rule-based analysis
    content_lower = block_content.lower()

    if any(w in content_lower for w in ["risk", "threat", "vulnerability", "concern"]):
        suggestions.append(Annotation(
            session_id=session_id,
            agent_id="risk-management",
            agent_name="Risk Agent",
            block_id=block_id,
            content="Consider adding a risk mitigation strategy and assigning a risk owner.",
            annotation_type="suggestion",
        ))

    if any(w in content_lower for w in ["budget", "cost", "expense", "spending"]):
        suggestions.append(Annotation(
            session_id=session_id,
            agent_id="financial-management",
            agent_name="Finance Agent",
            block_id=block_id,
            content="Financial items detected. Consider linking to the project budget baseline for variance tracking.",
            annotation_type="insight",
        ))

    if any(w in content_lower for w in ["deadline", "overdue", "delay", "behind schedule"]):
        suggestions.append(Annotation(
            session_id=session_id,
            agent_id="schedule-planning",
            agent_name="Schedule Agent",
            block_id=block_id,
            content="Schedule concern detected. Review the critical path and consider resource reallocation.",
            annotation_type="warning",
        ))

    if any(w in content_lower for w in ["quality", "defect", "bug", "issue"]):
        suggestions.append(Annotation(
            session_id=session_id,
            agent_id="quality-management",
            agent_name="Quality Agent",
            block_id=block_id,
            content="Quality issue referenced. Consider adding acceptance criteria and linking to the quality register.",
            annotation_type="suggestion",
        ))

    if len(block_content) > 500:
        suggestions.append(Annotation(
            session_id=session_id,
            agent_id="knowledge-management",
            agent_name="Knowledge Agent",
            block_id=block_id,
            content="This block contains substantial content. Consider breaking it into smaller, focused sections.",
            annotation_type="quality",
        ))

    return suggestions


async def _llm_suggest(content: str, context: dict[str, Any]) -> list[dict[str, Any]] | None:
    """Call LLM for annotation suggestions."""
    try:
        from llm.client import LLMGateway

        provider = os.getenv("LLM_PROVIDER", "mock")
        config: dict[str, Any] = {}
        if provider == "mock":
            config["demo_mode"] = True
        gateway = LLMGateway(provider=provider, config=config)

        system = (
            "You are an AI assistant for collaborative project editing. "
            "Analyze the content block and generate helpful annotations. "
            "Return a JSON array: "
            '[{"content":"...","type":"suggestion|warning|insight|quality",'
            '"agent_id":"...","agent_name":"..."}]. '
            "Available agents: risk-management, financial-management, "
            "schedule-planning, quality-management, knowledge-management, "
            "compliance-governance. Generate 1-3 annotations."
        )
        user = f"Content block:\n{content[:1000]}\n\nContext: {json.dumps(context)}"

        response = await gateway.complete(system, user, json_mode=True)
        raw = response.content.strip()
        if raw.startswith("```"):
            lines = raw.split("\n")
            lines = [line for line in lines if not line.strip().startswith("```")]
            raw = "\n".join(lines)
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return parsed
        if isinstance(parsed, dict) and "annotations" in parsed:
            return parsed["annotations"]
    except Exception as exc:
        logger.debug("LLM suggest call failed: %s", exc)

    return None
