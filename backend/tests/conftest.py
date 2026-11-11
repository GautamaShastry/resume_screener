import os

import httpx
import pytest

os.environ.setdefault("ENV", "test")

from app.core.services import build_services  # noqa: E402
from app.core.settings import Settings  # noqa: E402
from app.main import create_app  # noqa: E402


@pytest.fixture
def settings(tmp_path) -> Settings:
    return Settings(env="test", local_storage_dir=str(tmp_path / "blobs"), sse_poll_s=0.01)


@pytest.fixture
async def services(settings):
    svc = build_services(settings)
    yield svc
    await svc.aclose()


@pytest.fixture
async def client(services):
    app = create_app(services)
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c
