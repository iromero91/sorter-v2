from typing import Optional
from states.base_state import BaseState
from subsystems.shared_variables import SharedVariables
from .states import DistributionState
from irl.config import IRLInterface
from global_config import GlobalConfig


class Ready(BaseState):
    def __init__(self, irl: IRLInterface, gc: GlobalConfig, shared: SharedVariables):
        super().__init__(irl, gc)
        self.shared = shared
        self.signaled = False

    def step(self) -> Optional[DistributionState]:
        if not self.signaled:
            self.logger.info("Ready: distribution positioned, signaling ready")
            self.shared.distribution_ready = True
            self.signaled = True

        if not self.shared.distribution_ready:
            self.logger.info("Ready: piece dropped, moving to SENDING")
            return DistributionState.SENDING

        return None

    def cleanup(self) -> None:
        super().cleanup()
        self.signaled = False
