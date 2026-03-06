"""Tests for the execution events infrastructure (Enhancement 1)."""

from __future__ import annotations

import asyncio

import pytest

from agents.runtime.src.execution_events import (
    ExecutionEvent,
    ExecutionEventEmitter,
    ExecutionEventRegistry,
    ExecutionEventType,
)


@pytest.mark.asyncio
async def test_emitter_emit_and_get():
    emitter = ExecutionEventEmitter("corr-1")
    event = ExecutionEvent(
        event_type=ExecutionEventType.agent_started,
        task_id="t1",
        agent_id="a1",
    )
    await emitter.emit(event)
    received = await emitter.get(timeout=1.0)
    assert received is not None
    assert received.event_type == ExecutionEventType.agent_started
    assert received.task_id == "t1"
    assert received.correlation_id == "corr-1"


@pytest.mark.asyncio
async def test_emitter_complete_stops_iteration():
    emitter = ExecutionEventEmitter("corr-2")
    await emitter.emit(
        ExecutionEvent(event_type=ExecutionEventType.orchestration_started)
    )
    await emitter.complete()
    event = await emitter.get(timeout=1.0)
    assert event is not None
    assert event.event_type == ExecutionEventType.orchestration_started
    # Next get should return None (sentinel)
    sentinel = await emitter.get(timeout=1.0)
    assert sentinel is None


@pytest.mark.asyncio
async def test_emitter_get_timeout():
    emitter = ExecutionEventEmitter("corr-3")
    result = await emitter.get(timeout=0.05)
    assert result is None


def test_registry_create_and_get():
    registry = ExecutionEventRegistry()
    emitter = registry.create_emitter("test-corr")
    assert registry.get_emitter("test-corr") is emitter


def test_registry_remove():
    registry = ExecutionEventRegistry()
    registry.create_emitter("to-remove")
    registry.remove_emitter("to-remove")
    assert registry.get_emitter("to-remove") is None


def test_registry_get_nonexistent():
    registry = ExecutionEventRegistry()
    assert registry.get_emitter("nope") is None


def test_execution_event_model():
    event = ExecutionEvent(
        event_type=ExecutionEventType.agent_completed,
        task_id="t1",
        agent_id="agent-x",
        confidence_score=0.85,
        data={"success": True},
    )
    assert event.event_type == ExecutionEventType.agent_completed
    assert event.confidence_score == 0.85
    dumped = event.model_dump()
    assert dumped["agent_id"] == "agent-x"
