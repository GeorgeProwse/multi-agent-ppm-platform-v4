from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class PlanTask(BaseModel):
    model_config = ConfigDict(extra="allow")

    task_id: str
    agent_id: str
    action: str | None = None
    dependencies: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class Plan(BaseModel):
    model_config = ConfigDict(extra="allow")

    plan_id: str
    tasks: list[PlanTask]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    version: int = Field(ge=1)
