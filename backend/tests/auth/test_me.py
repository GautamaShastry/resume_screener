from sqlalchemy import func, select

from app.auth.models import User
from tests.helpers import auth


async def test_me_creates_user_once(client, db_session):
    r1 = await client.get("/api/me", headers=auth("me@example.com"))
    r2 = await client.get("/api/me", headers=auth("me@example.com"))
    assert r1.status_code == 200
    assert r1.json()["email"] == "me@example.com"
    assert r1.json()["plan"] == "free"
    assert r1.json()["id"] == r2.json()["id"]
    count = (await db_session.execute(select(func.count()).select_from(User))).scalar_one()
    assert count == 1


async def test_me_requires_bearer(client):
    r = await client.get("/api/me")
    assert r.status_code == 401
    assert r.json()["code"] == "UNAUTHORIZED"


async def test_dev_token_must_contain_email(client):
    r = await client.get("/api/me", headers={"Authorization": "Bearer dev:"})
    assert r.status_code == 401
