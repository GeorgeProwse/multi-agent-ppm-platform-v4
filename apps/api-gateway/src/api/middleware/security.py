from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx
import jwt
import yaml
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from jwt import InvalidTokenError
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("api-gateway-security")


@dataclass
class AuthContext:
    tenant_id: str
    subject: str
    roles: list[str]
    claims: dict[str, Any]


def _load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text())


def _load_rbac() -> tuple[dict[str, Any], dict[str, Any]]:
    repo_root = Path(__file__).resolve().parents[5]
    roles_cfg = _load_yaml(repo_root / "config" / "rbac" / "roles.yaml")
    field_cfg = _load_yaml(repo_root / "config" / "rbac" / "field-level.yaml")
    return roles_cfg, field_cfg


def _role_permissions(roles_cfg: dict[str, Any]) -> dict[str, set[str]]:
    return {role["id"]: set(role.get("permissions", [])) for role in roles_cfg.get("roles", [])}


def _required_permission(request: Request) -> str:
    path = request.url.path
    method = request.method
    if path.startswith("/api/v1/query"):
        return "workflow.execute"
    if path.startswith("/api/v1/agents"):
        return "workflow.read"
    if method in {"POST", "PUT", "PATCH", "DELETE"}:
        return "project.write"
    return "project.read"


def _classification_from_body(body: bytes) -> str | None:
    if not body:
        return None
    try:
        payload = json.loads(body.decode("utf-8"))
    except json.JSONDecodeError:
        return None
    if isinstance(payload, dict):
        return payload.get("classification")
    return None


def _is_classification_allowed(field_cfg: dict[str, Any], classification: str, roles: list[str]) -> bool:
    allowed_roles = (
        field_cfg.get("classification_access", {}).get(classification, {}).get("allowed_roles", [])
    )
    return any(role in allowed_roles for role in roles)


async def _validate_jwt(token: str) -> dict[str, Any]:
    identity_url = os.getenv("IDENTITY_ACCESS_URL")
    if identity_url:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(f"{identity_url}/auth/validate", json={"token": token})
            response.raise_for_status()
            data = response.json()
            if not data.get("active"):
                raise HTTPException(status_code=401, detail="Invalid token")
            return data.get("claims") or {}

    jwt_secret = os.getenv("IDENTITY_JWT_SECRET")
    jwks_url = os.getenv("IDENTITY_JWKS_URL")
    audience = os.getenv("IDENTITY_AUDIENCE")
    issuer = os.getenv("IDENTITY_ISSUER")
    try:
        if jwks_url:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(jwks_url)
                response.raise_for_status()
                jwks = response.json()
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get("kid")
            key = next((k for k in jwks.get("keys", []) if k.get("kid") == kid), None)
            if not key:
                raise HTTPException(status_code=401, detail="Invalid token key")
            public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))
            return jwt.decode(
                token,
                public_key,
                algorithms=[unverified_header.get("alg", "RS256")],
                audience=audience,
                issuer=issuer,
                options={"verify_aud": bool(audience), "verify_iss": bool(issuer)},
            )
        if not jwt_secret:
            raise HTTPException(status_code=500, detail="JWT validation configuration missing")
        return jwt.decode(
            token,
            jwt_secret,
            algorithms=["HS256"],
            audience=audience,
            issuer=issuer,
            options={"verify_aud": bool(audience), "verify_iss": bool(issuer)},
        )
    except InvalidTokenError as exc:
        logger.warning("token_validation_failed", extra={"error": str(exc)})
        raise HTTPException(status_code=401, detail="Invalid token") from exc


async def _evaluate_rbac(auth: AuthContext, permission: str, classification: str | None) -> None:
    policy_engine = os.getenv("POLICY_ENGINE_URL")
    if policy_engine:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                f"{policy_engine}/rbac/evaluate",
                json={
                    "tenant_id": auth.tenant_id,
                    "roles": auth.roles,
                    "permission": permission,
                    "classification": classification,
                },
            )
            response.raise_for_status()
            decision = response.json().get("decision")
            if decision != "allow":
                raise HTTPException(status_code=403, detail="RBAC denied")
        return

    roles_cfg, field_cfg = _load_rbac()
    role_permissions = _role_permissions(roles_cfg)
    allowed = any(permission in role_permissions.get(role, set()) for role in auth.roles)
    if classification and not _is_classification_allowed(field_cfg, classification, auth.roles):
        allowed = False
    if not allowed:
        raise HTTPException(status_code=403, detail="RBAC denied")


class AuthTenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        token = None
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "", 1).strip()
        tenant_id = request.headers.get("X-Tenant-ID")

        if not token or not tenant_id:
            return JSONResponse(status_code=401, content={"detail": "Missing JWT or tenant header"})

        try:
            claims = await _validate_jwt(token)
        except HTTPException as exc:
            return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

        roles = claims.get("roles") or claims.get("role") or []
        if isinstance(roles, str):
            roles = [roles]

        claim_tenant = claims.get("tenant_id")
        if claim_tenant and claim_tenant != tenant_id:
            return JSONResponse(status_code=403, content={"detail": "Tenant mismatch"})

        auth_context = AuthContext(
            tenant_id=tenant_id,
            subject=claims.get("sub", "unknown"),
            roles=roles,
            claims=claims,
        )
        request.state.auth = auth_context

        body = await request.body()
        request._body = body
        classification = _classification_from_body(body)
        permission = _required_permission(request)

        try:
            await _evaluate_rbac(auth_context, permission, classification)
        except HTTPException as exc:
            return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

        response = await call_next(request)
        return response
