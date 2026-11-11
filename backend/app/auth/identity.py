from dataclasses import dataclass
from typing import Protocol

import httpx

from app.auth.tokens import EntraTokenValidator
from app.core.errors import Unauthorized
from app.core.settings import Settings


@dataclass(frozen=True)
class Identity:
    oid: str
    email: str
    name: str


class Authenticator(Protocol):
    async def authenticate(self, token: str) -> Identity: ...


class DevAuthenticator:
    """Accepts tokens of the form `dev:<email>`. Only constructed when AUTH_MODE=dev."""

    async def authenticate(self, token: str) -> Identity:
        if not token.startswith("dev:") or "@" not in token[4:]:
            raise Unauthorized("Invalid dev token")
        email = token[4:].strip().lower()
        return Identity(oid=f"dev-{email}", email=email, name=email.split("@")[0])


class EntraAuthenticator:
    def __init__(self, validator: EntraTokenValidator):
        self._validator = validator

    async def authenticate(self, token: str) -> Identity:
        c = await self._validator.validate(token)
        if not c.get("oid"):
            raise Unauthorized("Token has no subject")
        emails = c.get("emails") or []
        email = c.get("email") or (emails[0] if emails else "") or c.get("preferred_username", "")
        return Identity(oid=c["oid"], email=email.lower(), name=c.get("name", ""))


def build_authenticator(settings: Settings, http: httpx.AsyncClient) -> Authenticator:
    if settings.auth_mode == "dev":
        return DevAuthenticator()
    return EntraAuthenticator(
        EntraTokenValidator(
            settings.entra_issuer, settings.entra_audience, settings.entra_jwks_url, http=http
        )
    )
