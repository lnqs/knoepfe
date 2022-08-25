from asyncio import Condition, Task, get_event_loop, sleep
from typing import Any, AsyncIterator, Awaitable, Callable, Dict, cast

from schema import Optional, Schema

from knoepfe import simpleobsws
from knoepfe.log import debug, info

config = Schema(
    {
        Optional("host"): str,
        Optional("port"): int,
        Optional("password"): str,
    }
)


class OBS:
    def __init__(self) -> None:
        self.ws = simpleobsws.WebSocketClient()
        self.ws.register_event_callback(self._handle_event)
        self.connection_watcher: Task[None] | None = None
        self.status_watcher: Task[None] | None = None
        self.streaming = False
        self.recording = False
        self.streaming_timecode = None
        self.recording_timecode = None
        self.current_scene: str | None = None

        self.last_event: Any = None
        self.event_condition = Condition()

    async def connect(self, config: Dict[str, Any]) -> None:
        if self.connection_watcher:
            return

        host = config.get("host", "localhost")
        port = config.get("port", 4444)
        password = cast(str, config.get("password"))
        self.ws.url = f"ws://{host}:{port}"
        self.ws.password = password

        loop = get_event_loop()
        self.connection_watcher = loop.create_task(self._watch_connection())

    @property
    def connected(self) -> bool:
        return bool(self.ws and self.ws.ws and self.ws.ws.open)

    async def listen(self) -> AsyncIterator[str]:
        while True:
            async with self.event_condition:
                await self.event_condition.wait()
                assert self.last_event
                event = self.last_event["eventType"]
            yield event

    async def start_recording(self) -> None:
        info("Starting OBS recording")
        await self.ws.call(simpleobsws.Request("StartRecord"))

    async def stop_recording(self) -> None:
        info("Stopping OBS recording")
        await self.ws.call(simpleobsws.Request("StopRecord"))

    async def start_streaming(self) -> None:
        info("Starting OBS streaming")
        await self.ws.call(simpleobsws.Request("StartStream"))

    async def stop_streaming(self) -> None:
        info("Stopping OBS streaming")
        await self.ws.call(simpleobsws.Request("StopStream"))

    async def set_scene(self, scene: str) -> None:
        if scene != self.current_scene:
            info(f"Setting current OBS scene to {scene}")
            await self.ws.call(
                simpleobsws.Request("SetCurrentProgramScene", {"sceneName": scene})
            )

    async def get_streaming_timecode(self) -> str | None:
        status = await self.ws.call(simpleobsws.Request("GetStreamStatus"))
        if status.ok():
            return cast(str, status.responseData["outputTimecode"])
        return None

    async def get_recording_timecode(self) -> str | None:
        status = await self.ws.call(simpleobsws.Request("GetRecordStatus"))
        if status.ok():
            return cast(str, status.responseData["outputTimecode"])
        return None

    async def _watch_connection(self) -> None:
        was_connected = False

        while True:
            if not self.connected and was_connected:
                debug("Connection to OBS lost")
                was_connected = False
                await self._handle_event(
                    {"eventType": "ConnectionLost"}
                )  # Fake connection lost event

            if not self.connected:
                try:
                    debug("Trying to connect to OBS")
                    await cast(Callable[[], Awaitable[bool]], self.ws.connect)()
                    if not await self.ws.wait_until_identified():
                        raise OSError("Failed to identify to OBS")
                    debug("Connected to OBS")
                    was_connected = True
                    await self._handle_event(
                        {"eventType": "ConnectionEstablished"}
                    )  # Fake connection established event
                except OSError as e:
                    debug(f"Failed to connect to OBS: {e}")

            await sleep(5.0)

    async def _handle_event(self, event: Dict[str, Any]) -> None:
        debug(f"OBS event received: {event}")
        if event["eventType"] == "ConnectionEstablished":
            self.current_scene = (
                await self.ws.call(simpleobsws.Request("GetCurrentProgramScene"))
            ).responseData["currentProgramSceneName"]
            self.streaming = (
                await self.ws.call(simpleobsws.Request("GetStreamStatus"))
            ).responseData["outputActive"]
            self.recording = (
                await self.ws.call(simpleobsws.Request("GetRecordStatus"))
            ).responseData["outputActive"]
            await self.get_recording_timecode()
        elif event["eventType"] == "CurrentProgramSceneChanged":
            self.current_scene = event["eventData"]["sceneName"]
        elif event["eventType"] == "StreamStateChanged":
            self.streaming = event["eventData"]["outputActive"]
        elif event["eventType"] == "RecordStateChanged":
            self.recording = event["eventData"]["outputActive"]
        elif event["eventType"] == "ConnectionLost":
            self.current_scene = None
            self.streaming = False
            self.recording = False

        async with self.event_condition:
            self.last_event = event
            self.event_condition.notify_all()


obs = OBS()
