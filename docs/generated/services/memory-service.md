# Memory Service

> Auto-generated from `services/memory_service/main.py`

## Overview

Conversation-context key-value store with optional TTL and SQLite persistence.

## Endpoints

| Method | Path | Description | Tags |
| --- | --- | --- | --- |
| `GET` | `/health` | Health check | health |
| `PUT` | `/contexts/{key}` | Persist a context dict under the given key | contexts |
| `GET` | `/contexts/{key}` | Retrieve a previously saved context by key | contexts |
| `DELETE` | `/contexts/{key}` | Delete a stored context | contexts |

## Configuration

| Environment Variable | Default | Description |
| --- | --- | --- |
| `MEMORY_SERVICE_BACKEND` | `memory` | Storage backend (`memory` or `sqlite`) |
| `MEMORY_SERVICE_SQLITE_PATH` | — | Path to SQLite database file |
| `MEMORY_SERVICE_DEFAULT_TTL_SECONDS` | `0` (no expiry) | Default TTL for stored contexts |

## Notes

- Does not follow the full service structure (no `helm/`, `contracts/`, or `Dockerfile`).
- Source files are at the top level of `services/memory_service/` rather than under a `src/` subdirectory.
