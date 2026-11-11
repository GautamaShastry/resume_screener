from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

import app.models_registry  # noqa: F401
from app.core.db import make_engine, make_sessionmaker
from app.core.settings import Settings


@dataclass
class Services:
    settings: Settings
    engine: AsyncEngine
    sessionmaker: async_sessionmaker[AsyncSession]

    async def aclose(self) -> None:
        await self.engine.dispose()


def build_services(settings: Settings) -> Services:
    engine = make_engine(settings)
    return Services(settings=settings, engine=engine, sessionmaker=make_sessionmaker(engine))
