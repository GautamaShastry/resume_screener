from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import AsyncSession

from app.llm.client import LLMUsage
from app.tasks.models import Task

if TYPE_CHECKING:
    from app.core.services import Services


@dataclass
class TaskResult:
    result_ref: dict
    quota_kind: str | None = None
    quota_count: int = 1


@dataclass
class TaskContext:
    task: Task
    session: AsyncSession
    services: "Services"
    usage: LLMUsage
    progress: Callable[[str], Awaitable[None]]


Handler = Callable[[TaskContext], Awaitable[TaskResult]]
FailureHook = Callable[[AsyncSession, Task], Awaitable[None]]


@dataclass
class Registration:
    handler: Handler
    steps: list[str] = field(default_factory=list)
    on_failed: FailureHook | None = None


class TaskRegistry:
    def __init__(self) -> None:
        self._items: dict[str, Registration] = {}

    def register(self, type_: str, steps: list[str], on_failed: FailureHook | None = None):
        def decorator(handler: Handler) -> Handler:
            self._items[type_] = Registration(handler, list(steps), on_failed)
            return handler

        return decorator

    def get(self, type_: str) -> Registration:
        return self._items[type_]


registry = TaskRegistry()
