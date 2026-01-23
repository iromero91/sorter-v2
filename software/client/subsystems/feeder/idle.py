from typing import Optional
from states.base_state import BaseState
from subsystems.shared_variables import SharedVariables
from .states import FeederState
from .frame_analysis import getNextFeederState
from irl.config import IRLInterface
from global_config import GlobalConfig
from vision.vision_manager import VisionManager


class Idle(BaseState):
    def __init__(
        self,
        irl: IRLInterface,
        gc: GlobalConfig,
        shared: SharedVariables,
        vision: VisionManager,
    ):
        super().__init__(irl, gc)
        self.shared = shared
        self.vision = vision

    def step(self) -> Optional[FeederState]:
        if not self.shared.classification_ready:
            return None

        masks_by_class = self.vision.getFeederMasksByClass()
        return getNextFeederState(masks_by_class, self.gc, FeederState.IDLE)

    def cleanup(self) -> None:
        super().cleanup()
