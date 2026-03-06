"""Copilot streaming endpoints — SSE-based real-time agent orchestration visibility."""

from __future__ import annotations

import asyncio
import json
import logging
import uuid
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

from agents.runtime.src.execution_events import (
    ExecutionEvent,
    ExecutionEventRegistry,
    ExecutionEventType,
)

logger = logging.getLogger("routes.copilot_stream")
router = APIRouter(tags=["copilot"])


class CopilotQueryRequest(BaseModel):
    query: str
    context: dict[str, Any] = Field(default_factory=dict)


class CopilotQueryResponse(BaseModel):
    correlation_id: str
    status: str = "streaming"


@router.post("/api/copilot/query")
async def copilot_query(request: CopilotQueryRequest) -> CopilotQueryResponse:
    """Accept a copilot query and return a correlation_id for SSE streaming."""
    correlation_id = str(uuid.uuid4())
    registry = ExecutionEventRegistry.get_instance()
    emitter = registry.create_emitter(correlation_id)

    await emitter.emit(
        ExecutionEvent(
            event_type=ExecutionEventType.orchestration_started,
            data={"query": request.query},
        )
    )

    return CopilotQueryResponse(correlation_id=correlation_id)


@router.get("/api/copilot/stream/{correlation_id}")
async def copilot_stream(correlation_id: str, request: Request) -> StreamingResponse:
    """SSE endpoint streaming execution events for a given correlation_id."""
    registry = ExecutionEventRegistry.get_instance()
    emitter = registry.get_emitter(correlation_id)

    async def event_generator():
        if emitter is None:
            yield _sse_format("error", {"message": "Unknown correlation_id"})
            return

        try:
            while True:
                if await request.is_disconnected():
                    break

                event = await emitter.get(timeout=15.0)
                if event is None:
                    yield _sse_format("heartbeat", {"ts": "keep-alive"})
                    continue

                yield _sse_format(
                    event.event_type.value,
                    event.model_dump(mode="json"),
                )

                if event.event_type == ExecutionEventType.orchestration_completed:
                    break
        finally:
            registry.remove_emitter(correlation_id)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


def _sse_format(event_type: str, data: dict[str, Any]) -> str:
    return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"
