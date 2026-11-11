from dataclasses import dataclass

import httpx
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

import app.models_registry  # noqa: F401
from app.auth.identity import Authenticator, build_authenticator
from app.core.db import make_engine, make_sessionmaker
from app.core.settings import Settings


@dataclass
class Services:
    settings: Settings
    engine: AsyncEngine
    sessionmaker: async_sessionmaker[AsyncSession]
    http: httpx.AsyncClient
    authenticator: Authenticator

    async def aclose(self) -> None:
        await self.http.aclose()
        await self.engine.dispose()


def build_services(settings: Settings) -> Services:
    engine = make_engine(settings)
    http = httpx.AsyncClient(timeout=10)
    return Services(
        settings=settings,
        engine=engine,
        sessionmaker=make_sessionmaker(engine),
        http=http,
        authenticator=build_authenticator(settings, http),
    )
