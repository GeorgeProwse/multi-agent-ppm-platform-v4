"""Event bus helpers for agent-to-agent communication."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Protocol

REPO_ROOT = Path(__file__).resolve().parents[3]
EVENT_BUS_SRC = REPO_ROOT / "packages" / "event_bus" / "src"
if EVENT_BUS_SRC.exists() and str(EVENT_BUS_SRC) not in sys.path:
    sys.path.insert(0, str(EVENT_BUS_SRC))

from event_bus import EventHandler, EventRecord, ServiceBusEventBus, get_event_bus


class EventBus(Protocol):
    def subscribe(self, topic: str, handler: EventHandler) -> None:
        ...

    async def publish(self, topic: str, payload: dict[str, Any]) -> None:
        ...

    def get_metrics(self) -> dict[str, int]:
        ...

    def get_recent_events(self, topic: str | None = None) -> list[EventRecord]:
        ...


__all__ = ["EventBus", "EventHandler", "EventRecord", "ServiceBusEventBus", "get_event_bus"]
