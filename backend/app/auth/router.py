import uuid

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.auth.deps import current_user
from app.auth.models import User

router = APIRouter(prefix="/api/me", tags=["me"])


class MeOut(BaseModel):
    id: uuid.UUID
    email: str
    name: str
    plan: str


@router.get("", response_model=MeOut)
async def get_me(user: User = Depends(current_user)) -> MeOut:
    return MeOut(id=user.id, email=user.email, name=user.name, plan=user.plan)
