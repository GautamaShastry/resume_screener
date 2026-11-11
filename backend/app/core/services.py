from dataclasses import dataclass

from app.core.settings import Settings


@dataclass
class Services:
    settings: Settings

    async def aclose(self) -> None:
        return None


def build_services(settings: Settings) -> Services:
    return Services(settings=settings)
