"""Tests for the NL workflow parser (Enhancement 3)."""

from __future__ import annotations

from nl_workflow import NLWorkflowParser


def test_parse_returns_valid_definition():
    parser = NLWorkflowParser()
    definition = parser.parse("Route incoming requests through risk assessment and approval")
    assert "name" in definition
    assert "steps" in definition
    assert len(definition["steps"]) > 0
    for step in definition["steps"]:
        assert "id" in step
        assert "type" in step
        assert "name" in step


def test_validate_valid_definition():
    parser = NLWorkflowParser()
    definition = parser.parse("test")
    result = parser.validate_generated(definition)
    assert result["valid"] is True
    assert result["errors"] == []


def test_validate_missing_name():
    parser = NLWorkflowParser()
    result = parser.validate_generated({"name": "", "steps": [{"id": "s1", "type": "task", "name": "x", "transitions": []}]})
    assert result["valid"] is False


def test_validate_bad_transition():
    parser = NLWorkflowParser()
    result = parser.validate_generated({
        "name": "test",
        "steps": [
            {"id": "s1", "type": "task", "name": "x", "transitions": [{"target": "nonexistent"}]}
        ],
    })
    assert result["valid"] is False
    assert any("nonexistent" in e for e in result["errors"])


def test_refine_returns_definition():
    parser = NLWorkflowParser()
    original = parser.parse("test")
    refined = parser.refine(original, "add a notification step")
    assert "steps" in refined
