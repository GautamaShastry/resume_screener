import os

from app.core.settings import Settings


def setup_telemetry(settings: Settings, role: str) -> bool:
    if not settings.applicationinsights_connection_string:
        return False
    os.environ.setdefault("OTEL_SERVICE_NAME", f"hireready-{role}")
    from azure.monitor.opentelemetry import configure_azure_monitor

    configure_azure_monitor(
        connection_string=settings.applicationinsights_connection_string, logger_name="app"
    )
    return True
