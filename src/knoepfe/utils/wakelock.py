from asyncio import Event


class WakeLock:
    def __init__(self, event: Event) -> None:
        self.count = 0
        self.event = event

    def acquire(self) -> None:
        self.count += 1
        if self.count == 1:
            self.event.set()

    def release(self) -> None:
        self.count -= 1
        assert self.count >= 0

    def held(self) -> bool:
        return self.count > 0
