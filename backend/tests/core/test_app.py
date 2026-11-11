import httpx
from fastapi import APIRouter
from pydantic import BaseModel

from app.core.errors import NotFound
from app.main import create_app


async def test_health(client):
    r = await client.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


async def test_app_error_envelope(services):
    app = create_app(services)
    router = APIRouter()

    @router.get("/api/boom")
    async def boom():
        raise NotFound("Thing not found", {"id": "x"})

    app.include_router(router)
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://t") as c:
        r = await c.get("/api/boom")
    assert r.status_code == 404
    assert r.json() == {"code": "NOT_FOUND", "message": "Thing not found", "details": {"id": "x"}}


async def test_validation_error_envelope(services):
    app = create_app(services)

    class Body(BaseModel):
        n: int

    @app.post("/api/echo")
    async def echo(body: Body):
        return body

    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://t") as c:
        r = await c.post("/api/echo", json={"n": "nope"})
    assert r.status_code == 422
    body = r.json()
    assert body["code"] == "VALIDATION"
    assert body["details"]["errors"][0]["loc"] == ["body", "n"]


async def test_unknown_route_envelope(client):
    r = await client.get("/api/does-not-exist")
    assert r.status_code == 404
    assert r.json()["code"] == "NOT_FOUND"


async def test_unhandled_exception_envelope(services):
    app = create_app(services)

    @app.get("/api/crash")
    async def crash():
        raise RuntimeError("secret internals")

    transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)
    async with httpx.AsyncClient(transport=transport, base_url="http://t") as c:
        r = await c.get("/api/crash")
    assert r.status_code == 500
    assert r.json() == {"code": "INTERNAL", "message": "Something went wrong", "details": {}}
