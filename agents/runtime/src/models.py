"""Shared agent request/response models."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AgentContext(BaseModel):
    """Standard context payload shared across agents."""

    model_config = ConfigDict(extra="allow")

    correlation_id: str | None = None
    tenant_id: str | None = None
    user_id: str | None = None


class AgentRequest(BaseModel):
    """Standard agent request wrapper."""

    model_config = ConfigDict(extra="allow")

    context: AgentContext | None = None
    correlation_id: str | None = None
    tenant_id: str | None = None
    policy_bundle: dict[str, Any] | None = None


class AgentPayload(BaseModel):
    """Typed agent payload envelope for arbitrary response data."""

    model_config = ConfigDict(extra="allow")


class AgentResponseMetadata(BaseModel):
    """Standard agent response metadata."""

    agent_id: str
    catalog_id: str
    timestamp: str
    correlation_id: str
    trace_id: str | None = None
    execution_time_seconds: float | None = None
    policy_reasons: tuple[str, ...] | None = None


class AgentResponse(BaseModel):
    """Standard agent response contract."""

    success: bool
    data: AgentPayload | None = None
    error: str | None = None
    metadata: AgentResponseMetadata


class AgentValidationError(BaseModel):
    """Standard validation error payload."""

    error: str
    details: list[dict[str, Any]] = Field(default_factory=list)
