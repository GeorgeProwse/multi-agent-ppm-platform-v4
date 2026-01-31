from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from event_bus import ServiceBusEventBus


@dataclass
class StubServiceBusMessage:
    body: str


class _StubSender:
    def __init__(self, sent: list[StubServiceBusMessage]) -> None:
        self._sent = sent

    async def __aenter__(self) -> "_StubSender":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> bool:
        return False

    async def send_messages(self, message: StubServiceBusMessage) -> None:
        self._sent.append(message)


class StubServiceBusClient:
    def __init__(self) -> None:
        self.sent: list[StubServiceBusMessage] = []

    async def __aenter__(self) -> "StubServiceBusClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> bool:
        return False

    def get_topic_sender(self, topic_name: str) -> _StubSender:
        return _StubSender(self.sent)


def build_test_event_bus() -> ServiceBusEventBus:
    return ServiceBusEventBus(
        connection_string="Endpoint=sb://local/;SharedAccessKeyName=local;SharedAccessKey=local",
        client=StubServiceBusClient(),
        message_cls=StubServiceBusMessage,
        local_dispatch=True,
    )
