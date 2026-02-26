"""Connector gallery routes (from legacy_main.py)."""
from __future__ import annotations

import json
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import JSONResponse

from routes._deps import (
    CONNECTOR_REGISTRY_PATH,
    _connector_hub_client,
    _passthrough_response,
    _require_session,
    _tenant_id_from_request,
    build_forward_headers,
    logger,
)
from routes._models import ConnectorInstanceCreate, ConnectorInstanceUpdate

router = APIRouter()


def _load_connector_registry() -> list[dict[str, Any]]:
    if not CONNECTOR_REGISTRY_PATH.exists():
        return []
    try:
        with CONNECTOR_REGISTRY_PATH.open("r", encoding="utf-8") as f:
            payload = json.load(f)
    except (OSError, json.JSONDecodeError):
        return []
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        return list(payload.get("connectors", []))
    return []


@router.get("/api/connector-gallery/types")
async def list_connector_types(request: Request) -> list[dict[str, Any]]:
    session = _require_session(request)
    tenant_id = _tenant_id_from_request(request, session)
    types = _load_connector_registry()
    logger.info("connector_gallery.types.list", extra={"tenant_id": tenant_id})
    return types


@router.get("/api/connector-gallery/instances")
async def list_connector_instances(request: Request) -> Response:
    session = _require_session(request)
    tenant_id = _tenant_id_from_request(request, session)
    headers = build_forward_headers(request, session)
    client = _connector_hub_client()
    try:
        response = await client.list_connectors(headers=headers)
    except httpx.RequestError:
        raise HTTPException(status_code=504, detail="Connector hub unavailable")
    logger.info("connector_gallery.instances.list", extra={"tenant_id": tenant_id})
    if response.status_code >= 400:
        return _passthrough_response(response)
    return JSONResponse(status_code=response.status_code, content=response.json())


@router.post("/api/connector-gallery/instances")
async def create_connector_instance(payload: ConnectorInstanceCreate, request: Request) -> Response:
    session = _require_session(request)
    tenant_id = _tenant_id_from_request(request, session)
    headers = build_forward_headers(request, session)
    metadata = {"connector_type_id": payload.connector_type_id}
    metadata.update(payload.metadata or {})
    connector_request = {"name": payload.connector_type_id, "version": payload.version, "enabled": payload.enabled, "metadata": metadata}
    client = _connector_hub_client()
    try:
        response = await client.create_connector(connector_request, headers=headers)
    except httpx.RequestError:
        raise HTTPException(status_code=504, detail="Connector hub unavailable")
    if response.status_code >= 400:
        return _passthrough_response(response)
    body = response.json()
    logger.info("connector_gallery.instances.create", extra={"tenant_id": tenant_id, "connector_id": body.get("connector_id"), "connector_type_id": payload.connector_type_id})
    return JSONResponse(status_code=response.status_code, content=body)


@router.patch("/api/connector-gallery/instances/{connector_id}")
async def update_connector_instance(connector_id: str, payload: ConnectorInstanceUpdate, request: Request) -> Response:
    session = _require_session(request)
    tenant_id = _tenant_id_from_request(request, session)
    headers = build_forward_headers(request, session)
    update_payload = payload.model_dump(exclude_none=True)
    client = _connector_hub_client()
    try:
        response = await client.update_connector(connector_id, update_payload, headers=headers)
    except httpx.RequestError:
        raise HTTPException(status_code=504, detail="Connector hub unavailable")
    if response.status_code >= 400:
        return _passthrough_response(response)
    body = response.json()
    logger.info("connector_gallery.instances.update", extra={"tenant_id": tenant_id, "connector_id": connector_id, "connector_type_id": body.get("metadata", {}).get("connector_type_id")})
    return JSONResponse(status_code=response.status_code, content=body)


@router.get("/api/connector-gallery/instances/{connector_id}/health")
async def get_connector_health(connector_id: str, request: Request) -> Response:
    session = _require_session(request)
    tenant_id = _tenant_id_from_request(request, session)
    headers = build_forward_headers(request, session)
    client = _connector_hub_client()
    try:
        response = await client.get_connector_health(connector_id, headers=headers)
    except httpx.RequestError:
        raise HTTPException(status_code=504, detail="Connector hub unavailable")
    if response.status_code >= 400:
        return _passthrough_response(response)
    body = response.json()
    logger.info("connector_gallery.instances.health", extra={"tenant_id": tenant_id, "connector_id": connector_id, "connector_type_id": body.get("metadata", {}).get("connector_type_id")})
    return JSONResponse(status_code=response.status_code, content=body)
