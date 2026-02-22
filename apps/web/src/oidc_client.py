from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import httpx
import jwt
from fastapi import HTTPException
from jwt import InvalidTokenError


@dataclass(frozen=True)
class OIDCDiscovery:
    issuer: str
    authorization_endpoint: str
    token_endpoint: str
    jwks_uri: str
    end_session_endpoint: str | None = None


class OIDCClient:
    def __init__(
        self,
        *,
        issuer_url: str,
        client_id: str,
        client_secret: str | None,
        redirect_uri: str,
        scope: str,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self.issuer_url = issuer_url.rstrip("/")
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scope = scope
        self._transport = transport
        self._discovery: OIDCDiscovery | None = None

    async def discover(self) -> OIDCDiscovery:
        if self._discovery:
            return self._discovery
        well_known = f"{self.issuer_url}/.well-known/openid-configuration"
        try:
            async with httpx.AsyncClient(timeout=10.0, transport=self._transport) as client:
                response = await client.get(well_known)
                response.raise_for_status()
                payload = response.json()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=502,
                detail=f"OIDC discovery failed: HTTP {exc.response.status_code}",
            ) from exc
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=502,
                detail="OIDC provider unreachable during discovery",
            ) from exc
        self._discovery = OIDCDiscovery(
            issuer=payload["issuer"],
            authorization_endpoint=payload["authorization_endpoint"],
            token_endpoint=payload["token_endpoint"],
            jwks_uri=payload["jwks_uri"],
            end_session_endpoint=payload.get("end_session_endpoint"),
        )
        return self._discovery

    async def exchange_code(self, code: str) -> dict[str, Any]:
        discovery = await self.discover()
        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
        }
        if self.client_secret:
            payload["client_secret"] = self.client_secret
        try:
            async with httpx.AsyncClient(timeout=10.0, transport=self._transport) as client:
                response = await client.post(discovery.token_endpoint, data=payload)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=502,
                detail=f"OIDC token exchange failed: HTTP {exc.response.status_code}",
            ) from exc
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=502,
                detail="OIDC provider unreachable during token exchange",
            ) from exc

    async def verify_id_token(self, id_token: str, nonce: str | None) -> dict[str, Any]:
        discovery = await self.discover()
        try:
            async with httpx.AsyncClient(timeout=10.0, transport=self._transport) as client:
                response = await client.get(discovery.jwks_uri)
                response.raise_for_status()
                jwks = response.json()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=502,
                detail=f"OIDC JWKS fetch failed: HTTP {exc.response.status_code}",
            ) from exc
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=502,
                detail="OIDC JWKS endpoint unreachable",
            ) from exc

        unverified_header = jwt.get_unverified_header(id_token)
        kid = unverified_header.get("kid")
        key = next((k for k in jwks.get("keys", []) if k.get("kid") == kid), None)
        if not key:
            raise HTTPException(status_code=401, detail="OIDC signing key not found")

        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))
        try:
            claims = jwt.decode(
                id_token,
                public_key,
                algorithms=[unverified_header.get("alg", "RS256")],
                audience=self.client_id,
                issuer=discovery.issuer,
                options={"verify_aud": True, "verify_iss": True},
            )
        except InvalidTokenError as exc:
            raise HTTPException(status_code=401, detail="Invalid OIDC token") from exc

        if nonce and claims.get("nonce") != nonce:
            raise HTTPException(status_code=401, detail="Invalid OIDC nonce")

        return claims
