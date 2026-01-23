from defs.sorter_controller import SorterLifecycle
from irl.config import IRLInterface
from global_config import GlobalConfig
from coordinator import Coordinator
from vision import VisionManager
import queue


class SorterController:
    def __init__(
        self,
        irl: IRLInterface,
        gc: GlobalConfig,
        vision: VisionManager,
        event_queue: queue.Queue,
    ):
        self.state = SorterLifecycle.INITIALIZING
        self.irl = irl
        self.gc = gc
        self.vision = vision
        self.event_queue = event_queue
        self.coordinator = Coordinator(irl, gc, vision, event_queue)

    def start(self) -> None:
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
