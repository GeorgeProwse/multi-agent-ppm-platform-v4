"""
Pydantic-style models and protocol classes for the Data Synchronization Agent.
"""

from collections.abc import Mapping
from typing import Protocol


class SecretContext(Protocol):
    def get(self, name: str) -> str | None: ...

    def set_many(self, values: Mapping[str, str]) -> None: ...

    def snapshot(self) -> dict[str, str]: ...


class InMemorySecretContext:
    def __init__(self, initial: Mapping[str, str] | None = None) -> None:
        self._values = dict(initial or {})

    def get(self, name: str) -> str | None:
        return self._values.get(name)

    def set_many(self, values: Mapping[str, str]) -> None:
        self._values.update(values)

    def snapshot(self) -> dict[str, str]:
        return dict(self._values)
