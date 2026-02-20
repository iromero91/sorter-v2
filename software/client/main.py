from global_config import mkGlobalConfig, GlobalConfig
from runtime_variables import mkRuntimeVariables
from server.api import (
    app,
    broadcastEvent,
    setRuntimeVariables,
    setCommandQueue,
    setController,
)
from sorter_controller import SorterController
from message_queue.handler import handleServerToMainEvent
from defs.events import HeartbeatEvent, HeartbeatData, MainThreadToServerCommand
import toml
from hardware.sorter_hardware import SorterHardware
from vision import VisionManager
from subsystems.distribution.bin_layout import mkDefaultLayout
from subsystems.distribution.chute import Chute
import uvicorn
import threading
import queue
import time
import asyncio
import sys

SHUTDOWN_MOTOR_STOP_DELAY_MS = 100
FRAME_BROADCAST_INTERVAL_MS = 100

server_to_main_queue = queue.Queue()
main_to_server_queue = queue.Queue()


def runServer() -> None:
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="error", ws="wsproto")


def runBroadcaster(gc: GlobalConfig) -> None:
    import server.api as api

    while api.server_loop is None:
        time.sleep(0.01)

    while True:
        try:
            command = main_to_server_queue.get(block=False)
            if command.tag != "frame":
                gc.logger.info(f"broadcasting {command.tag} event")
            asyncio.run_coroutine_threadsafe(
                broadcastEvent(command.model_dump()), api.server_loop
            )
        except queue.Empty:
            pass

        time.sleep(gc.timeouts.main_loop_sleep_ms / 1000.0)


def main() -> None:
    gc = mkGlobalConfig()
    rv = mkRuntimeVariables(gc)
    setRuntimeVariables(rv)
    setCommandQueue(server_to_main_queue)
    # Load hardware config from TOML
    hardware_config = toml.load("hardware/system_config.toml")
    hardware = SorterHardware(hardware_config)

    layout = mkDefaultLayout()
    chute = Chute(gc, hardware.steppers["chute"], layout)
    gc.logger.info("Homing chute to zero...")
    chute.home()

    vision = VisionManager(gc)  # Remove irl_config dependency if possible
    controller = SorterController(hardware, gc, vision, main_to_server_queue, rv)
    setController(controller)
    gc.logger.info("client starting...")

    vision.start()
    controller.start()

    server_thread = threading.Thread(target=runServer, daemon=True)
    server_thread.start()

    broadcaster_thread = threading.Thread(
        target=runBroadcaster, args=(gc,), daemon=True
    )
    broadcaster_thread.start()

    last_heartbeat = time.time()
    last_frame_broadcast = time.time()

    try:
        while True:
            try:
                event = server_to_main_queue.get(block=False)
                handleServerToMainEvent(gc, controller, hardware, event)
            except queue.Empty:
                pass

            current_time = time.time()

            # send periodic heartbeat
            # can probably remove this later, just helps debug web sockets from time to time
            if (
                current_time - last_heartbeat
                >= gc.timeouts.heartbeat_interval_ms / 1000.0
            ):
                heartbeat = HeartbeatEvent(
                    tag="heartbeat", data=HeartbeatData(timestamp=current_time)
                )
                main_to_server_queue.put(heartbeat)
                last_heartbeat = current_time

            # broadcast camera frames and record to disk
            if (
                current_time - last_frame_broadcast
                >= FRAME_BROADCAST_INTERVAL_MS / 1000.0
            ):
                for frame_event in vision.getAllFrameEvents():
                    main_to_server_queue.put(frame_event)
                vision.recordFrames()
                last_frame_broadcast = current_time

            controller.step()

            time.sleep(gc.timeouts.main_loop_sleep_ms / 1000.0)
    except KeyboardInterrupt:
        gc.logger.info("Shutting down...")

        vision.stop()

        # Send motor shutdown commands and wait for them to complete
        gc.logger.info("Stopping all motors...")
        hardware.shutdown_all()
        gc.logger.info("Cleanup complete")
        sys.exit(0)


if __name__ == "__main__":
    main()
