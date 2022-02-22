import asyncio
from asyncio import Condition, Task, get_event_loop, sleep
from typing import Any, AsyncIterator, Dict, cast

import obswebsocket
from obswebsocket import obsws, requests
from obswebsocket.base_classes import Baseevents, Baserequests
from obswebsocket.events import (
    RecordingStarted,
    RecordingStopped,
    StreamStarted,
    StreamStopped,
    SwitchScenes,
)
from schema import Optional, Schema

from knoepfe.log import debug, info

config = Schema(
    {
        Optional("host"): str,
        Optional("port"): int,
        Optional("password"): str,
    }
)


class ConnectionEstablished(Baseevents):  # type: ignore
    def __init__(self) -> None:
        obswebsocket.events.Baseevents.__init__(self)
        self.name = "ConnectionEstablished"


class ConnectionLost(Baseevents):  # type: ignore
    def __init__(self) -> None:
        obswebsocket.events.Baseevents.__init__(self)
        self.name = "ConnectionLost"


class StreamingStatus(Baseevents):  # type: ignore
    def __init__(self) -> None:
        obswebsocket.events.Baseevents.__init__(self)
        self.name = "StreamingStatus"


class OBS:
    def __init__(self) -> None:
        self.obsws = obsws()
        self.connection_watcher: Task[None] | None = None

        loop = get_event_loop()

        self.streaming_status: Any | None = None
        self.streaming_status_watcher: Task[None] | None = None
        self.current_scene: str | None = None

        self.last_event = None
        self.event_condition = Condition()

        self.obsws.register(
            lambda *args: asyncio.run_coroutine_threadsafe(
                self.handle_event(*args), loop
            )
        )

    @property
    def connected(self) -> bool:
        return bool(self.obsws.ws and self.obsws.ws.connected)

    @property
    def recording(self) -> bool:
        return bool(self.streaming_status and self.streaming_status.getRecording())

    @property
    def recording_timecode(self) -> str | None:
        if self.streaming_status:
            try:
                return cast(str, self.streaming_status.getRecTimecode())
            except KeyError:
                pass
        return None

    @property
    def streaming(self) -> bool:
        return bool(self.streaming_status and self.streaming_status.getStreaming())

    @property
    def streaming_timecode(self) -> str | None:
        if self.streaming_status:
            try:
                return cast(str, self.streaming_status.getStreamTimecode())
            except KeyError:
                pass
        return None

    async def connect(self, config: Dict[str, Any]) -> None:
        if self.connection_watcher:
            return

        self.obsws.host = config.get("host", "localhost")
        self.obsws.port = config.get("port", 4444)
        self.obsws.password = config.get("password")

        loop = get_event_loop()
        self.connection_watcher = loop.create_task(self.watch_connection())

    async def listen(self) -> AsyncIterator[str]:
        while True:
            async with self.event_condition:
                await self.event_condition.wait()
                assert self.last_event
                event = self.last_event.name
            yield event

    async def start_recording(self) -> None:
        info("Starting OBS recording")
        await self.perform_request(requests.StartRecording())

    async def stop_recording(self) -> None:
        info("Stopping OBS recording")
        await self.perform_request(requests.StopRecording())

    async def start_streaming(self) -> None:
        info("Starting OBS streaming")
        await self.perform_request(requests.StartStreaming())

    async def stop_streaming(self) -> None:
        info("Stopping OBS streaming")
        await self.perform_request(requests.StopStreaming())

    async def set_scene(self, scene: str) -> None:
        if scene != self.current_scene:
            info(f"Setting current OBS scene to {scene}")
            await self.perform_request(requests.SetCurrentScene(scene))

    async def watch_connection(self) -> None:
        was_connected = False

        while True:
            if not self.connected and was_connected:
                debug("Connection to OBS lost")
                self.obsws.eventmanager.trigger(ConnectionLost())
                was_connected = False

            if not self.connected:
                try:
                    debug("Trying to connect to OBS")
                    self.obsws.connect()
                    debug("Connected to OBS")
                    self.obsws.eventmanager.trigger(ConnectionEstablished())
                    was_connected = True
                except obswebsocket.exceptions.ConnectionFailure:
                    debug("Failed to connect to OBS")

            await sleep(3.0)

    async def watch_streaming_status(self) -> None:
        while True:
            if self.connected:
                status = self.obsws.call(requests.GetStreamingStatus())
                if (
                    not self.streaming_status
                    or status.datain != self.streaming_status.datain
                ):
                    self.streaming_status = status
                    self.obsws.eventmanager.trigger(StreamingStatus())
            if (
                not self.connected
                or not self.streaming_status
                or (
                    not self.streaming_status.getRecording()
                    and not self.streaming_status.getStreaming()
                )
            ):
                self.streaming_status = None
                self.streaming_status_watcher = None
                return
            await sleep(1.0)

    async def handle_event(self, event: Baseevents) -> None:
        debug(f"OBS event received: {event.name}")

        if isinstance(event, (ConnectionEstablished, StreamStarted, RecordingStarted)):
            self.streaming_status = self.obsws.call(requests.GetStreamingStatus())
            self.current_scene = self.obsws.call(requests.GetCurrentScene()).getName()
            if not self.streaming_status_watcher:
                self.streaming_status_watcher = get_event_loop().create_task(
                    self.watch_streaming_status()
                )
        elif isinstance(event, (StreamStopped, RecordingStopped)):
            self.streaming_status = self.obsws.call(requests.GetStreamingStatus())
        elif isinstance(event, SwitchScenes):
            self.current_scene = event.getSceneName()
        elif isinstance(event, ConnectionLost):
            self.streaming_status = None
            self.current_scene = None

        async with self.event_condition:
            self.last_event = event
            self.event_condition.notify_all()

    async def perform_request(self, request: Baserequests) -> None:
        if self.connected:
            self.obsws.call(request)


obs = OBS()
