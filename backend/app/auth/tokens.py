import time

import httpx
import jwt
from jwt import PyJWK, PyJWKSet

from app.core.errors import Unauthorized


class EntraTokenValidator:
    def __init__(
        self,
        issuer: str,
        audience: str,
        jwks_url: str,
        http: httpx.AsyncClient,
        cache_ttl_s: float = 3600.0,
        min_refresh_interval_s: float = 60.0,
    ):
        self._issuer = issuer
        self._audience = audience
        self._jwks_url = jwks_url
        self._http = http
        self._ttl = cache_ttl_s
        self._min_interval = min_refresh_interval_s
        self._keys: dict[str, PyJWK] = {}
        self._fetched_at = float("-inf")

    async def _refresh(self) -> None:
        r = await self._http.get(self._jwks_url, timeout=10)
        r.raise_for_status()
        self._keys = {k.key_id: k for k in PyJWKSet.from_dict(r.json()).keys if k.key_id}
        self._fetched_at = time.monotonic()

    async def validate(self, token: str) -> dict:
        try:
            kid = jwt.get_unverified_header(token).get("kid")
        except jwt.PyJWTError as exc:
            raise Unauthorized("Invalid token") from exc
        age = time.monotonic() - self._fetched_at
        if age > self._ttl or (kid not in self._keys and age > self._min_interval):
            await self._refresh()
        key = self._keys.get(kid or "")
        if key is None:
            raise Unauthorized("Unknown signing key")
        try:
            return jwt.decode(
                token,
                key.key,
                algorithms=["RS256"],
                audience=self._audience,
                issuer=self._issuer,
                options={"require": ["exp", "iss", "aud"]},
            )
        except jwt.PyJWTError as exc:
            raise Unauthorized("Invalid token") from exc
