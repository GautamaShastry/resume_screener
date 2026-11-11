from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth.router import router as me_router
from app.core.errors import install_error_handlers
from app.core.logging import setup_logging
from app.core.services import Services, build_services
from app.core.settings import get_settings

health_router = APIRouter()


@health_router.get("/api/health", include_in_schema=False)
async def health() -> dict:
    return {"status": "ok"}


def create_app(services: Services, *, close_on_shutdown: bool = False) -> FastAPI:
    @asynccontextmanager
    async def lifespan(_: FastAPI):
        yield
        if close_on_shutdown:
            await services.aclose()

    app = FastAPI(title="HireReady API", version="2.0.0", lifespan=lifespan)
    app.state.services = services
    app.add_middleware(
        CORSMiddleware,
        allow_origins=services.settings.cors_origins,
        allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
    )
    install_error_handlers(app)
    app.include_router(health_router)
    app.include_router(me_router)
    return app


def build_app() -> FastAPI:
    settings = get_settings()
    setup_logging()
    return create_app(build_services(settings), close_on_shutdown=True)
