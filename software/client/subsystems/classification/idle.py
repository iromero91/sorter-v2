from typing import Optional
from states.base_state import BaseState
from subsystems.shared_variables import SharedVariables
from .states import ClassificationState
from .carousel import Carousel
from hardware.sorter_hardware import SorterHardware
from global_config import GlobalConfig


class Idle(BaseState):
    def __init__(
        self,
        hardware: SorterHardware,
        gc: GlobalConfig,
        shared: SharedVariables,
        carousel: Carousel,
    ):
        super().__init__(hardware, gc)
        self.shared = shared
        self.carousel = carousel

    def step(self) -> Optional[ClassificationState]:
        if self.shared.classification_ready:
            return ClassificationState.DETECTING
        return None

    def cleanup(self) -> None:
        super().cleanup()
