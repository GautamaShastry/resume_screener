import socket

import pytest

from app.core.settings import Settings
from app.tasks.queue import AzureTaskQueue, InMemoryQueue
from tests.storage.test_blob import AZURITE


class Clock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


async def test_in_memory_visibility_and_dequeue_count():
    clock = Clock()
    q = InMemoryQueue(clock=clock)
    await q.send({"task_id": "1"})
    [m1] = await q.receive(10, 30)
    assert m1.dequeue_count == 1
    assert await q.receive(10, 30) == []  # invisible
    clock.t = 31
    [m2] = await q.receive(10, 30)
    assert m2.dequeue_count == 2
    await q.delete(m1)  # stale receipt: ignored
    assert len(q) == 1
    m3 = await q.extend(m2, 60)
    await q.delete(m3)
    assert len(q) == 0


def _azurite_up() -> bool:
    try:
        socket.create_connection(("127.0.0.1", 10001), timeout=0.5).close()
        return True
    except OSError:
        return False


@pytest.mark.azure
@pytest.mark.skipif(not _azurite_up(), reason="Azurite not running")
async def test_azure_queue_roundtrip():
    s = Settings(
        env="test",
        queue_mode="azure",
        azure_storage_connection_string=AZURITE,
        queue_name="test-tasks",
        poison_queue_name="test-tasks-poison",
    )
    q = AzureTaskQueue.from_settings(s)
    await q.ensure()
    try:
        await q.send({"task_id": "abc"})
        msgs = await q.receive(1, 5)
        assert msgs[0].body == {"task_id": "abc"}
        extended = await q.extend(msgs[0], 5)
        await q.delete(extended)
        await q.send_poison({"task_id": "abc"})
    finally:
        await q.aclose()
