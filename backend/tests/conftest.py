import asyncio
import os
import pathlib
import subprocess
import sys

import httpx
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

TEST_DB = os.environ.get(
    "TEST_DATABASE_URL", "postgresql+asyncpg://hireready:hireready@localhost:5433/hireready_test"
)
os.environ["DATABASE_URL"] = TEST_DB
os.environ.setdefault("ENV", "test")
BACKEND_DIR = pathlib.Path(__file__).resolve().parents[1]

from app.core.db import Base  # noqa: E402
from app.core.services import build_services  # noqa: E402
from app.core.settings import Settings  # noqa: E402
from app.main import create_app  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def migrated_db():
    async def reset() -> None:
        eng = create_async_engine(TEST_DB)
        async with eng.begin() as conn:
            await conn.execute(text("DROP SCHEMA public CASCADE"))
            await conn.execute(text("CREATE SCHEMA public"))
        await eng.dispose()

    asyncio.run(reset())
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        check=True,
        cwd=BACKEND_DIR,
        env={**os.environ, "DATABASE_URL": TEST_DB},
    )


@pytest.fixture
def settings(tmp_path) -> Settings:
    return Settings(
        env="test", database_url=TEST_DB, local_storage_dir=str(tmp_path / "blobs"), sse_poll_s=0.01
    )


@pytest.fixture
async def services(settings):
    svc = build_services(settings)
    yield svc
    tables = ", ".join(t.name for t in Base.metadata.sorted_tables)
    async with svc.engine.begin() as conn:
        await conn.execute(text(f"TRUNCATE {tables} CASCADE"))
    await svc.aclose()


@pytest.fixture
async def db_session(services):
    async with services.sessionmaker() as session:
        yield session


@pytest.fixture
def make_user(db_session):
    from app.auth.models import User

    async def _make(email: str = "a@example.com") -> User:
        user = User(entra_oid=f"oid-{email}", email=email, name=email.split("@")[0])
        db_session.add(user)
        await db_session.commit()
        return user

    return _make


@pytest.fixture
async def client(services):
    app = create_app(services)
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c
