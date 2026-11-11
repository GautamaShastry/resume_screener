import uuid

from fastapi import APIRouter, Depends, Response, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.deps import current_user
from app.auth.models import User
from app.auth.service import delete_account
from app.core.deps import get_services, get_session
from app.core.services import Services
from app.quotas.service import next_reset, usage_today

router = APIRouter(prefix="/api/me", tags=["me"])


class MeOut(BaseModel):
    id: uuid.UUID
    email: str
    name: str
    plan: str


class UsageItem(BaseModel):
    used: int
    limit: int


class UsageOut(BaseModel):
    resets_at: str
    items: dict[str, UsageItem]


@router.get("", response_model=MeOut)
async def get_me(user: User = Depends(current_user)) -> MeOut:
    return MeOut(id=user.id, email=user.email, name=user.name, plan=user.plan)


@router.get("/usage", response_model=UsageOut)
async def get_usage(
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_session),
    services: Services = Depends(get_services),
) -> UsageOut:
    items = await usage_today(session, services.settings, user.id)
    return UsageOut(resets_at=next_reset().isoformat(), items=items)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_me(
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_session),
    services: Services = Depends(get_services),
) -> Response:
    await delete_account(session, services, user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
