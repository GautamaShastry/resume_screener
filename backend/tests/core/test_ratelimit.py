import pytest

from app.core.errors import RateLimited
from app.core.ratelimit import RateLimiter
from app.core.settings import Settings
from app.core.telemetry import setup_telemetry
from tests.helpers import auth


def test_sliding_window():
    now = [0.0]
    rl = RateLimiter(2, clock=lambda: now[0])
    rl.hit("u")
    rl.hit("u")
    with pytest.raises(RateLimited):
        rl.hit("u")
    rl.hit("other")
    now[0] = 61
    rl.hit("u")


async def test_api_returns_429_after_limit(client, services):
    services.rate_limiter = RateLimiter(3)
    for _ in range(3):
        assert (await client.get("/api/me", headers=auth())).status_code == 200
    r = await client.get("/api/me", headers=auth())
    assert r.status_code == 429 and r.json()["code"] == "RATE_LIMITED"


def test_telemetry_noop_without_connection_string():
    assert setup_telemetry(Settings(env="test"), "api") is False
