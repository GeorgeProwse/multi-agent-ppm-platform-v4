"""Tests for intake intelligence (Enhancement 6)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

# Import _simple_similarity directly to avoid triggering routes/__init__.py
_mod_path = Path(__file__).resolve().parents[2] / "apps" / "web" / "src" / "routes" / "intake_intelligence.py"
_spec = importlib.util.spec_from_file_location("intake_intelligence", _mod_path)
_mod = importlib.util.module_from_spec(_spec)
sys.modules["intake_intelligence"] = _mod
_spec.loader.exec_module(_mod)
_simple_similarity = _mod._simple_similarity


def test_simple_similarity_identical():
    score = _simple_similarity("hello world", "hello world")
    assert score == 1.0


def test_simple_similarity_different():
    score = _simple_similarity("hello world", "foo bar")
    assert score == 0.0


def test_simple_similarity_partial():
    score = _simple_similarity("cloud migration finance", "cloud migration azure")
    assert 0 < score < 1


def test_simple_similarity_empty():
    assert _simple_similarity("", "hello") == 0.0
    assert _simple_similarity("hello", "") == 0.0
