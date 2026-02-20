from subsystems import (
    SharedVariables,
    FeederStateMachine,
    ClassificationStateMachine,
    DistributionStateMachine,
    mkDefaultLayout,
    layoutMatchesCategories,
    applyCategories,
)
from hardware.sorter_hardware import SorterHardware
from global_config import GlobalConfig
from runtime_variables import RuntimeVariables
from vision import VisionManager
from sorting_profile import BrickLinkCategories
from blob_manager import getBinCategories
import queue


class Coordinator:
    def __init__(
        self,
        hardware: SorterHardware,
        gc: GlobalConfig,
        vision: VisionManager,
        event_queue: queue.Queue,
        rv: RuntimeVariables,
    ):
        self.hardware = hardware
        self.gc = gc
        self.logger = gc.logger
        self.vision = vision
        self.event_queue = event_queue
        self.shared = SharedVariables()
        self.sorting_profile = BrickLinkCategories(gc)
        self.distribution_layout = mkDefaultLayout()

        saved_categories = getBinCategories()
        if saved_categories is not None:
            if layoutMatchesCategories(self.distribution_layout, saved_categories):
                applyCategories(self.distribution_layout, saved_categories)
                self.logger.info("Loaded bin categories from storage")
            else:
                self.logger.warn("Saved bin categories don't match layout, ignoring")

        self.distribution = DistributionStateMachine(
            hardware,
            gc,
            self.shared,
            self.sorting_profile,
            self.distribution_layout,
            event_queue,
        )
        self.classification = ClassificationStateMachine(
            hardware, gc, self.shared, vision, event_queue
        )
        self.feeder = FeederStateMachine(hardware, gc, self.shared, vision)

    def step(self) -> None:
        self.feeder.step()
        self.classification.step()
        self.distribution.step()

    def cleanup(self) -> None:
        self.feeder.cleanup()
        self.classification.cleanup()
        self.distribution.cleanup()
