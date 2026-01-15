import time
from typing import Optional
from states.base_state import BaseState
from subsystems.shared_variables import SharedVariables
from .states import ClassificationState
from irl.config import IRLInterface
from global_config import GlobalConfig

CLASSIFY_DURATION_MS = 300


class Classifying(BaseState):
    def __init__(self, irl: IRLInterface, gc: GlobalConfig, shared: SharedVariables):
        super().__init__(irl, gc)
        self.shared = shared
        self.classification_done = False

    def step(self) -> Optional[ClassificationState]:
        self._ensureExecutionThreadStarted()

        if self.classification_done:
            if self.shared.distribution_ready:
                self.shared.distribution_ready = False
                self.shared.piece_at_distribution = True
                self.shared.classification_ready = True
                return ClassificationState.IDLE
        return None

    def cleanup(self) -> None:
        super().cleanup()
        self.classification_done = False

    def _executionLoop(self) -> None:
        self.logger.info("Classification: classifying piece")
        time.sleep(CLASSIFY_DURATION_MS / 1000.0)
        if self._stop_event.is_set():
            return
        self.logger.info("Classification: done")
        self.classification_done = True
