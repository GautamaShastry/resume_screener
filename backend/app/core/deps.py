from collections.abc import AsyncIterator

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.services import Services


def get_services(request: Request) -> Services:
    return request.app.state.services


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    async with request.app.state.services.sessionmaker() as session:
        yield session
