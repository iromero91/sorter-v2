from subsystems.base_subsystem import BaseSubsystem
from subsystems.shared_variables import SharedVariables
from .states import ClassificationState
from .idle import Idle
from .classifying import Classifying
from irl.config import IRLInterface
from global_config import GlobalConfig


class ClassificationStateMachine(BaseSubsystem):
    def __init__(self, irl: IRLInterface, gc: GlobalConfig, shared: SharedVariables):
        super().__init__()
        self.irl = irl
        self.gc = gc
        self.logger = gc.logger
        self.shared = shared
        self.current_state = ClassificationState.IDLE
        self.states_map = {
            ClassificationState.IDLE: Idle(irl, gc, shared),
            ClassificationState.CLASSIFYING: Classifying(irl, gc, shared),
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
