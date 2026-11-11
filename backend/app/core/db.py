from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.settings import Settings

PG_ENTRA_SCOPE = "https://ossrdbms-aad.database.windows.net/.default"


class Base(DeclarativeBase):
    pass


def make_engine(settings: Settings) -> AsyncEngine:
    engine = create_async_engine(settings.database_url, pool_pre_ping=True)
    if settings.db_auth == "entra":
        from azure.identity import DefaultAzureCredential

        credential = DefaultAzureCredential()

        @event.listens_for(engine.sync_engine, "do_connect")
        def _inject_token(dialect, conn_rec, cargs, cparams):  # noqa: ANN001
            cparams["user"] = settings.db_entra_user
            cparams["password"] = credential.get_token(PG_ENTRA_SCOPE).token

    return engine


def make_sessionmaker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False)
