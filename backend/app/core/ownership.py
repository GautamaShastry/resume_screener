import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFound


async def get_owned[M](
    session: AsyncSession, model: type[M], obj_id: uuid.UUID, user_id: uuid.UUID
) -> M:
    obj = await session.get(model, obj_id)
    if obj is None or obj.user_id != user_id:  # type: ignore[attr-defined]
        raise NotFound(f"{model.__name__} not found")
    return obj
