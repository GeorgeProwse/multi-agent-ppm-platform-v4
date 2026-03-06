"""Tests for collaborative editing annotations (Enhancement 8)."""

from __future__ import annotations

from annotations import Annotation, AnnotationStore


def test_create_annotation():
    store = AnnotationStore()
    ann = Annotation(agent_id="risk-agent", agent_name="Risk Management", block_id="b1", content="Consider adding risk mitigation", annotation_type="suggestion")
    created = store.create_annotation("session-1", ann)
    assert created.session_id == "session-1"
    assert created.annotation_id.startswith("ann-")


def test_list_annotations():
    store = AnnotationStore()
    store.create_annotation("s1", Annotation(content="a"))
    store.create_annotation("s1", Annotation(content="b"))
    store.create_annotation("s2", Annotation(content="c"))
    assert len(store.list_annotations("s1")) == 2
    assert len(store.list_annotations("s2")) == 1


def test_dismiss_annotation():
    store = AnnotationStore()
    ann = store.create_annotation("s1", Annotation(content="dismiss me"))
    store.dismiss_annotation(ann.annotation_id)
    active = store.list_annotations("s1", active_only=True)
    assert len(active) == 0
    all_anns = store.list_annotations("s1", active_only=False)
    assert len(all_anns) == 1
    assert all_anns[0].dismissed is True


def test_apply_annotation():
    store = AnnotationStore()
    ann = store.create_annotation("s1", Annotation(content="apply me"))
    result = store.apply_annotation(ann.annotation_id)
    assert result is not None
    assert result.applied is True


def test_dismiss_nonexistent():
    store = AnnotationStore()
    assert store.dismiss_annotation("nope") is None
