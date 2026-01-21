from typing import Optional
from states.base_state import BaseState
from subsystems.shared_variables import SharedVariables
from .states import ClassificationState
from irl.config import IRLInterface
from global_config import GlobalConfig


class Idle(BaseState):
    def __init__(self, irl: IRLInterface, gc: GlobalConfig, shared: SharedVariables):
        super().__init__(irl, gc)
        self.shared = shared

    def step(self) -> Optional[ClassificationState]:
        if not self.shared.classification_ready:
            return ClassificationState.CLASSIFYING
        return None

    def cleanup(self) -> None:
        super().cleanup()
