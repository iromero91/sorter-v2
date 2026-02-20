from defs.sorter_controller import SorterLifecycle
from hardware.sorter_hardware import SorterHardware
from global_config import GlobalConfig
from runtime_variables import RuntimeVariables
from coordinator import Coordinator
from vision import VisionManager
import queue


class SorterController:
    def __init__(
        self,
        hardware: SorterHardware,
        gc: GlobalConfig,
        vision: VisionManager,
        event_queue: queue.Queue,
        rv: RuntimeVariables,
    ):
        self.state = SorterLifecycle.INITIALIZING
        self.hardware = hardware
        self.gc = gc
        self.vision = vision
        self.event_queue = event_queue
        self.coordinator = Coordinator(hardware, gc, vision, event_queue, rv)

    def start(self) -> None:
        self.state = SorterLifecycle.PAUSED

    def resume(self) -> None:
        self.state = SorterLifecycle.RUNNING

    def pause(self) -> None:
        self.coordinator.cleanup()
        self.state = SorterLifecycle.PAUSED

    def stop(self) -> None:
        self.coordinator.cleanup()
        self.state = SorterLifecycle.READY

    def step(self) -> None:
        if self.state == SorterLifecycle.RUNNING:
            self.coordinator.step()
