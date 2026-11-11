"""Usage: python -m app.scripts.export_openapi > ../frontend/openapi.json"""

import json
import sys

from app.core.services import build_services
from app.core.settings import Settings
from app.main import create_app


def main() -> None:
    # The schema needs no database; ignore any DATABASE_URL in the environment.
    settings = Settings(env="local", database_url="postgresql+asyncpg://unused/unused")
    app = create_app(build_services(settings))
    json.dump(app.openapi(), sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
