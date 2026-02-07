"""Shared event bus implementations."""

from __future__ import annotations

import os
from typing import Final

from event_bus.models import EventHandler, EventRecord
from event_bus.service_bus import ServiceBusEventBus

_DEFAULT_TOPIC: Final[str] = "ppm-events"
_EVENT_BUS: ServiceBusEventBus | None = None


def get_event_bus() -> ServiceBusEventBus:
    """Return a singleton Service Bus-backed event bus using environment configuration."""
    global _EVENT_BUS
    if _EVENT_BUS is None:
        connection_string = os.getenv("AZURE_SERVICE_BUS_CONNECTION_STRING") or os.getenv(
            "SERVICE_BUS_CONNECTION_STRING"
        )
        if not connection_string:
            raise ValueError(
                "AZURE_SERVICE_BUS_CONNECTION_STRING must be set to initialize the event bus."
            )
        topic_name = os.getenv("SERVICE_BUS_QUEUE_NAME") or os.getenv(
            "EVENT_BUS_TOPIC", _DEFAULT_TOPIC
        )
        subscription_name = os.getenv("SERVICE_BUS_SUBSCRIPTION_NAME") or os.getenv(
            "EVENT_BUS_SUBSCRIPTION"
        )
        _EVENT_BUS = ServiceBusEventBus(
            connection_string=connection_string,
            topic_name=topic_name,
            subscription_name=subscription_name,
        )
    return _EVENT_BUS


__all__ = ["EventHandler", "EventRecord", "ServiceBusEventBus", "get_event_bus"]
