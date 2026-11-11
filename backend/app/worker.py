import asyncio
import contextlib
import logging
import signal
import time
import uuid

from opentelemetry import propagate, trace

from app.core.logging import setup_logging
from app.core.services import Services, build_services
from app.core.settings import get_settings
from app.core.telemetry import setup_telemetry
from app.tasks.queue import QueueMessage
from app.tasks.registry import TaskRegistry, registry
from app.tasks.runner import Lease, process_message, recover_stuck, renew_lease

VISIBILITY_S = 300
RENEW_EVERY_S = 120
RECOVER_EVERY_S = 60
log = logging.getLogger("app.worker")
tracer = trace.get_tracer("app.worker")


async def _renew(services: Services, lease: Lease) -> None:
    task_id = uuid.UUID(lease.msg.body["task_id"])
    while True:
        await asyncio.sleep(RENEW_EVERY_S)
        try:
            lease.msg = await services.queue.extend(lease.msg, VISIBILITY_S)
            await renew_lease(services, task_id)
        except Exception:  # noqa: BLE001  (a transient error must not end renewal)
            log.warning("lease_renew_failed", extra={"task_id": str(task_id)}, exc_info=True)


async def _run_one(services: Services, reg: TaskRegistry, msg: QueueMessage) -> None:
    lease = Lease(msg)
    renewer = asyncio.create_task(_renew(services, lease))
    try:
        with tracer.start_as_current_span("task", context=propagate.extract(msg.body)):
            await process_message(services, reg, lease)
    except Exception:  # noqa: BLE001
        log.exception("worker_message_error")
    finally:
        renewer.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await renewer


async def run_worker(
    services: Services,
    reg: TaskRegistry,
    *,
    stop: asyncio.Event,
    concurrency: int = 4,
    poll_interval: float = 2.0,
) -> None:
    await recover_stuck(services)
    last_recovery = time.monotonic()
    running: set[asyncio.Task] = set()
    while not stop.is_set():
        if time.monotonic() - last_recovery > RECOVER_EVERY_S:
            last_recovery = time.monotonic()
            try:
                await recover_stuck(services)
            except Exception:  # noqa: BLE001
                log.exception("recover_stuck_failed")
        free = concurrency - len(running)
        messages = await services.queue.receive(free, VISIBILITY_S) if free > 0 else []
        for msg in messages:
            t = asyncio.create_task(_run_one(services, reg, msg))
            running.add(t)
            t.add_done_callback(running.discard)
        if not messages:
            with contextlib.suppress(TimeoutError):
                await asyncio.wait_for(stop.wait(), timeout=poll_interval)
    if running:
        await asyncio.gather(*running, return_exceptions=True)


def main() -> None:
    import app.tasks.handlers  # noqa: F401  (registers handlers)

    settings = get_settings()
    setup_logging()
    setup_telemetry(settings, "worker")
    services = build_services(settings)
    stop = asyncio.Event()

    async def runner() -> None:
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            with contextlib.suppress(NotImplementedError):
                loop.add_signal_handler(sig, stop.set)
        if settings.env != "prod":
            await services.queue.ensure()
            await services.blob.ensure()
        log.info("worker_started")
        try:
            await run_worker(services, registry, stop=stop)
        finally:
            await services.aclose()

    asyncio.run(runner())


if __name__ == "__main__":
    main()
