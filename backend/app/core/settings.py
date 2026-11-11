from functools import lru_cache
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_QUOTAS = {
    "resume_upload": 10,
    "posting_import": 30,
    "analysis": 20,
    "tailoring": 10,
    "practice_session": 5,
    "practice_answer": 30,
    "recommendation": 3,
}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    env: Literal["local", "test", "prod"] = "local"

    database_url: str = "postgresql+asyncpg://hireready:hireready@localhost:5433/hireready"
    db_auth: Literal["password", "entra"] = "password"
    db_entra_user: str = ""

    auth_mode: Literal["dev", "entra"] = "dev"
    entra_issuer: str = ""
    entra_jwks_url: str = ""
    entra_audience: str = ""

    storage_mode: Literal["local", "azure"] = "local"
    local_storage_dir: str = ".data/blobs"
    azure_storage_account_url: str = ""
    azure_queue_account_url: str = ""
    azure_storage_connection_string: str = ""
    blob_container: str = "resumes"

    queue_mode: Literal["memory", "azure"] = "memory"
    queue_name: str = "tasks"
    poison_queue_name: str = "tasks-poison"

    llm_provider: Literal["fake", "azure_openai"] = "fake"
    azure_openai_endpoint: str = ""
    azure_openai_api_version: str = "2024-10-21"
    azure_openai_chat_deployment: str = "chat"
    llm_timeout_s: float = 60.0

    cors_origins: list[str] = ["http://localhost:5173"]
    rate_limit_per_min: int = 60
    sse_poll_s: float = 1.0
    task_retry_backoff_s: float = 15.0
    applicationinsights_connection_string: str = ""

    quota_limits: dict[str, int] = Field(default_factory=lambda: dict(DEFAULT_QUOTAS))

    @model_validator(mode="after")
    def _prod_requires_cloud_components(self) -> "Settings":
        if self.env == "prod":
            bad = []
            if self.auth_mode != "entra":
                bad.append("AUTH_MODE=entra")
            if self.storage_mode != "azure":
                bad.append("STORAGE_MODE=azure")
            if self.queue_mode != "azure":
                bad.append("QUEUE_MODE=azure")
            if self.llm_provider != "azure_openai":
                bad.append("LLM_PROVIDER=azure_openai")
            if bad:
                raise ValueError("ENV=prod requires " + ", ".join(bad))
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
