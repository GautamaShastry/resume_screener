from app.tasks.registry import TaskRegistry
from app.tasks.registry import registry as global_registry
from app.tasks.runner import Lease, process_message


def auth(email: str = "a@example.com") -> dict[str, str]:
    return {"Authorization": f"Bearer dev:{email}"}


async def drain(services, registry: TaskRegistry = global_registry, rounds: int = 10) -> None:
    """Process queued messages until the queue is empty (visibility 0 → failures retry at once)."""
    for _ in range(rounds):
        messages = await services.queue.receive(10, 0)
        if not messages:
            return
        for message in messages:
            await process_message(services, registry, Lease(message))
