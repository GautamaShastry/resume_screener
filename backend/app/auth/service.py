from typing import TYPE_CHECKING

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.identity import Identity
from app.auth.models import User

if TYPE_CHECKING:
    from app.core.services import Services


async def upsert_user(session: AsyncSession, identity: Identity) -> User:
    stmt = (
        insert(User)
        .values(entra_oid=identity.oid, email=identity.email, name=identity.name)
        .on_conflict_do_update(
            index_elements=[User.entra_oid],
            set_={"email": identity.email, "name": identity.name},
        )
        .returning(User)
    )
    user = (await session.execute(stmt)).scalar_one()
    await session.commit()
    return user


async def delete_account(session: AsyncSession, services: "Services", user: User) -> None:
    await services.blob.delete_prefix(f"resumes/{user.id}/")
    await session.delete(user)
    await session.commit()
