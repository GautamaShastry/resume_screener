from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.auth.service import upsert_user
from app.core.deps import get_services, get_session
from app.core.errors import Unauthorized
from app.core.services import Services


async def current_user(
    request: Request,
    services: Services = Depends(get_services),
    session: AsyncSession = Depends(get_session),
) -> User:
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        raise Unauthorized("Missing bearer token")
    identity = await services.authenticator.authenticate(header[7:].strip())
    user = await upsert_user(session, identity)
    services.rate_limiter.hit(user.id)
    return user
