import json
import time

import httpx
import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from jwt.algorithms import RSAAlgorithm

from app.auth.tokens import EntraTokenValidator
from app.core.errors import Unauthorized

ISS = "https://tenant.ciamlogin.com/tid/v2.0"
AUD = "api-client-id"
JWKS_URL = "https://tenant.ciamlogin.com/tid/discovery/v2.0/keys"


def _keypair(kid: str):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    jwk = json.loads(RSAAlgorithm.to_jwk(key.public_key()))
    jwk.update({"kid": kid, "use": "sig", "alg": "RS256"})
    return key, jwk


def _token(key, kid, **overrides):
    claims = {
        "iss": ISS,
        "aud": AUD,
        "exp": int(time.time()) + 300,
        "oid": "user-1",
        "email": "u@example.com",
        "name": "U",
    }
    claims.update(overrides)
    return jwt.encode(claims, key, algorithm="RS256", headers={"kid": kid})


def _validator(jwks: list[dict], calls: list[int]):
    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(1)
        return httpx.Response(200, json={"keys": jwks})

    http = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    return EntraTokenValidator(ISS, AUD, JWKS_URL, http=http)


async def test_valid_token_returns_claims():
    key, jwk = _keypair("k1")
    v = _validator([jwk], [])
    claims = await v.validate(_token(key, "k1"))
    assert claims["oid"] == "user-1"


@pytest.mark.parametrize(
    "overrides", [{"aud": "other"}, {"iss": "https://evil/v2.0"}, {"exp": int(time.time()) - 10}]
)
async def test_rejects_bad_claims(overrides):
    key, jwk = _keypair("k1")
    v = _validator([jwk], [])
    with pytest.raises(Unauthorized):
        await v.validate(_token(key, "k1", **overrides))


async def test_rejects_wrong_signature():
    key, jwk = _keypair("k1")
    other, _ = _keypair("k1")
    v = _validator([jwk], [])
    with pytest.raises(Unauthorized):
        await v.validate(_token(other, "k1"))


async def test_unknown_kid_refreshes_at_most_once_per_minute():
    key, jwk = _keypair("k1")
    calls: list[int] = []
    v = _validator([jwk], calls)
    await v.validate(_token(key, "k1"))
    with pytest.raises(Unauthorized):
        await v.validate(_token(key, "missing"))
    with pytest.raises(Unauthorized):
        await v.validate(_token(key, "missing"))
    assert len(calls) == 1


async def test_garbage_token():
    _, jwk = _keypair("k1")
    v = _validator([jwk], [])
    with pytest.raises(Unauthorized):
        await v.validate("not-a-jwt")
