import time
from collections import defaultdict, deque
from collections.abc import Callable, Hashable

from app.core.errors import RateLimited

WINDOW_S = 60.0


class RateLimiter:
    """Per-key sliding window. Per-process; sufficient with 1–3 API replicas."""

    def __init__(self, per_minute: int, clock: Callable[[], float] = time.monotonic):
        self.per_minute = per_minute
        self._clock = clock
        self._hits: dict[Hashable, deque[float]] = defaultdict(deque)

    def hit(self, key: Hashable) -> None:
        now = self._clock()
        window = self._hits[key]
        while window and now - window[0] >= WINDOW_S:
            window.popleft()
        if len(window) >= self.per_minute:
            raise RateLimited("Too many requests. Try again in a minute.")
        window.append(now)
