from subsystems.base_subsystem import BaseSubsystem
from subsystems.shared_variables import SharedVariables
from .states import ClassificationState
from .idle import Idle
from .detecting import Detecting
from .rotating import Rotating
from .snapping import Snapping
from .carousel import Carousel
from hardware.sorter_hardware import SorterHardware
from global_config import GlobalConfig
from vision import VisionManager
import queue


class ClassificationStateMachine(BaseSubsystem):
    def __init__(
        self,
        hardware: SorterHardware,
        gc: GlobalConfig,
        shared: SharedVariables,
        vision: VisionManager,
        event_queue: queue.Queue,
    ):
        super().__init__()
        self.hardware = hardware
        self.gc = gc
        self.logger = gc.logger
        self.shared = shared
        self.vision = vision
        self.event_queue = event_queue
        self.carousel = Carousel(gc.logger, event_queue)
        self.current_state = ClassificationState.IDLE

        # Replace irl.carousel_stepper with hardware.steppers["carousel"]
        self.states_map = {
            ClassificationState.IDLE: Idle(hardware, gc, shared, self.carousel),
            ClassificationState.DETECTING: Detecting(
                hardware, gc, shared, self.carousel, vision
            ),
            ClassificationState.ROTATING: Rotating(
                hardware, gc, shared, self.carousel, hardware.steppers["carousel"], event_queue
            ),
            ClassificationState.SNAPPING: Snapping(
                hardware, gc, shared, self.carousel, vision, event_queue
            ),
        }

    def step(self) -> None:
        next_state = self.states_map[self.current_state].step()
        if next_state and next_state != self.current_state:
            self.logger.info(
                f"Classification: {self.current_state.value} -> {next_state.value}"
            )
            self.states_map[self.current_state].cleanup()
            self.current_state = next_state

    def cleanup(self) -> None:
        self.states_map[self.current_state].cleanup()
