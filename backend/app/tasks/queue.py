import json
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol

from azure.core.exceptions import ResourceExistsError
from azure.storage.queue.aio import QueueClient

from app.core.settings import Settings


@dataclass
class QueueMessage:
    id: str
    pop_receipt: str
    body: dict
    dequeue_count: int


class TaskQueue(Protocol):
    async def send(self, body: dict) -> None: ...
    async def receive(self, max_messages: int, visibility_timeout: int) -> list[QueueMessage]: ...
    async def delete(self, msg: QueueMessage) -> None: ...
    async def extend(self, msg: QueueMessage, visibility_timeout: int) -> QueueMessage: ...
    async def send_poison(self, body: dict) -> None: ...
    async def ensure(self) -> None: ...
    async def aclose(self) -> None: ...


class InMemoryQueue:
    def __init__(self, clock: Callable[[], float] = time.monotonic):
        self._items: dict[str, dict] = {}
        self._clock = clock
        self.poison: list[dict] = []

    def __len__(self) -> int:
        return len(self._items)

    async def send(self, body: dict) -> None:
        self._items[uuid.uuid4().hex] = {
            "body": dict(body),
            "visible_at": float("-inf"),
            "dequeue_count": 0,
            "receipt": "",
        }

    async def receive(self, max_messages: int, visibility_timeout: int) -> list[QueueMessage]:
        now = self._clock()
        out: list[QueueMessage] = []
        for mid, item in self._items.items():
            if len(out) >= max_messages:
                break
            if item["visible_at"] <= now:
                item["dequeue_count"] += 1
                item["receipt"] = uuid.uuid4().hex
                item["visible_at"] = now + visibility_timeout
                out.append(
                    QueueMessage(mid, item["receipt"], dict(item["body"]), item["dequeue_count"])
                )
        return out

    async def delete(self, msg: QueueMessage) -> None:
        item = self._items.get(msg.id)
        if item and item["receipt"] == msg.pop_receipt:
            del self._items[msg.id]

    async def extend(self, msg: QueueMessage, visibility_timeout: int) -> QueueMessage:
        item = self._items[msg.id]
        if item["receipt"] != msg.pop_receipt:
            raise RuntimeError("Lost lease on message")
        item["receipt"] = uuid.uuid4().hex
        item["visible_at"] = self._clock() + visibility_timeout
        return QueueMessage(msg.id, item["receipt"], msg.body, msg.dequeue_count)

    async def send_poison(self, body: dict) -> None:
        self.poison.append(dict(body))

    async def ensure(self) -> None:
        return None

    async def aclose(self) -> None:
        return None


class AzureTaskQueue:
    def __init__(self, main: QueueClient, poison: QueueClient):
        self._main = main
        self._poison = poison

    @classmethod
    def from_settings(cls, settings: Settings) -> "AzureTaskQueue":
        if settings.azure_storage_connection_string:

            def make(name: str) -> QueueClient:
                return QueueClient.from_connection_string(
                    settings.azure_storage_connection_string, name
                )
        else:
            from azure.identity.aio import DefaultAzureCredential

            credential = DefaultAzureCredential()

            def make(name: str) -> QueueClient:
                return QueueClient(settings.azure_queue_account_url, name, credential=credential)

        return cls(make(settings.queue_name), make(settings.poison_queue_name))

    async def send(self, body: dict) -> None:
        await self._main.send_message(json.dumps(body))

    async def receive(self, max_messages: int, visibility_timeout: int) -> list[QueueMessage]:
        out: list[QueueMessage] = []
        async for m in self._main.receive_messages(
            messages_per_page=max_messages,
            visibility_timeout=max(visibility_timeout, 1),
            max_messages=max_messages,
        ):
            out.append(
                QueueMessage(m.id, m.pop_receipt or "", json.loads(m.content), m.dequeue_count or 0)
            )
        return out

    async def delete(self, msg: QueueMessage) -> None:
        await self._main.delete_message(msg.id, msg.pop_receipt)

    async def extend(self, msg: QueueMessage, visibility_timeout: int) -> QueueMessage:
        updated = await self._main.update_message(
            msg.id, pop_receipt=msg.pop_receipt, visibility_timeout=visibility_timeout
        )
        return QueueMessage(msg.id, updated.pop_receipt or "", msg.body, msg.dequeue_count)

    async def send_poison(self, body: dict) -> None:
        await self._poison.send_message(json.dumps(body))

    async def ensure(self) -> None:
        for client in (self._main, self._poison):
            try:
                await client.create_queue()
            except ResourceExistsError:
                pass

    async def aclose(self) -> None:
        await self._main.close()
        await self._poison.close()


def build_queue(settings: Settings) -> TaskQueue:
    if settings.queue_mode == "azure":
        return AzureTaskQueue.from_settings(settings)
    return InMemoryQueue()
