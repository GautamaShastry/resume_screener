import pytest
from pydantic import ValidationError

from app.core.settings import Settings


def test_defaults_are_local_friendly():
    s = Settings(env="test")
    assert s.auth_mode == "dev"
    assert s.quota_limits["analysis"] == 20
    assert s.quota_limits["recommendation"] == 3


def test_prod_rejects_dev_components():
    with pytest.raises(ValidationError):
        Settings(env="prod", auth_mode="dev")


def test_prod_accepts_azure_components():
    s = Settings(
        env="prod",
        auth_mode="entra",
        storage_mode="azure",
        queue_mode="azure",
        llm_provider="azure_openai",
    )
    assert s.env == "prod"
