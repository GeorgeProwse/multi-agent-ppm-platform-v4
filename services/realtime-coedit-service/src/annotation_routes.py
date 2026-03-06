"""REST API routes for agent annotations in collaborative editing sessions."""

from __future__ import annotations

from fastapi import APIRouter

from annotations import (
    Annotation,
    get_annotation_store,
)

router = APIRouter(prefix="/v1/sessions", tags=["annotations"])


@router.post("/{session_id}/annotations")
async def create_annotation(session_id: str, annotation: Annotation) -> Annotation:
    store = get_annotation_store()
    return store.create_annotation(session_id, annotation)


@router.get("/{session_id}/annotations")
async def list_annotations(session_id: str) -> list[Annotation]:
    store = get_annotation_store()
    return store.list_annotations(session_id)


@router.post("/{session_id}/annotations/{annotation_id}/dismiss")
async def dismiss_annotation(session_id: str, annotation_id: str) -> dict:
    store = get_annotation_store()
    ann = store.dismiss_annotation(annotation_id)
    return {"dismissed": ann is not None, "annotation_id": annotation_id}


@router.post("/{session_id}/annotations/{annotation_id}/apply")
async def apply_annotation(session_id: str, annotation_id: str) -> dict:
    store = get_annotation_store()
    ann = store.apply_annotation(annotation_id)
    return {"applied": ann is not None, "annotation_id": annotation_id}
