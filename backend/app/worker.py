import asyncio
import contextlib
import logging
import signal

from opentelemetry import propagate, trace

from app.core.logging import setup_logging
from app.core.services import Services, build_services
from app.core.settings import get_settings
from app.tasks.queue import QueueMessage
from app.tasks.registry import TaskRegistry, registry
from app.tasks.runner import Lease, process_message, recover_stuck

VISIBILITY_S = 300
RENEW_EVERY_S = 120
log = logging.getLogger("app.worker")
tracer = trace.get_tracer("app.worker")


async def _renew(services: Services, lease: Lease) -> None:
    while True:
        await asyncio.sleep(RENEW_EVERY_S)
        lease.msg = await services.queue.extend(lease.msg, VISIBILITY_S)


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
    running: set[asyncio.Task] = set()
    while not stop.is_set():
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
