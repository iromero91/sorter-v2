from defs.sorter_controller import SorterLifecycle
from irl.config import IRLInterface
from global_config import GlobalConfig
from coordinator import Coordinator


class SorterController:
    def __init__(self, irl: IRLInterface, gc: GlobalConfig):
        self.state = SorterLifecycle.INITIALIZING
        self.irl = irl
        self.gc = gc
        self.coordinator = Coordinator(irl, gc)

    def start(self) -> None:
        self.state = SorterLifecycle.RUNNING
        self.coordinator.triggerStart()

    def pause(self) -> None:
        self.coordinator.cleanup()
        self.state = SorterLifecycle.PAUSED

    def stop(self) -> None:
        self.coordinator.cleanup()
        self.state = SorterLifecycle.READY

    def step(self) -> None:
        if self.state == SorterLifecycle.RUNNING:
            self.coordinator.step()
