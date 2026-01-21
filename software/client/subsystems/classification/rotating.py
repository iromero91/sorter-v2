from typing import Optional, TYPE_CHECKING
import time
from states.base_state import BaseState
from subsystems.shared_variables import SharedVariables
from .states import ClassificationState
from .carousel import Carousel
from irl.config import IRLInterface
from global_config import GlobalConfig

if TYPE_CHECKING:
    from irl.stepper import Stepper

ROTATE_DURATION_MS = 1000


class Rotating(BaseState):
    def __init__(
        self,
        irl: IRLInterface,
        gc: GlobalConfig,
        shared: SharedVariables,
        carousel: Carousel,
        stepper: "Stepper",
    ):
        super().__init__(irl, gc)
        self.shared = shared
        self.carousel = carousel
        self.stepper = stepper
        self.start_time: Optional[float] = None
        self.command_sent = False

    def step(self) -> Optional[ClassificationState]:
        if self.start_time is None:
            self.start_time = time.time()
            self.logger.info("Rotating: starting rotation")
            self.stepper.rotate(-90.0)
            self.command_sent = True

        elapsed_ms = (time.time() - self.start_time) * 1000
        if elapsed_ms < ROTATE_DURATION_MS:
            return None

        self.logger.info("Rotating: rotation complete")
        exiting = self.carousel.rotate()
        if exiting:
            if exiting.part_id is not None:
                self.logger.info(
                    f"Rotating: handing off {exiting.uuid[:8]} ({exiting.part_id}) to distribution"
                )
                self.shared.distribution_ready = False
                self.shared.exiting_piece = exiting
            else:
                self.logger.info(
                    f"Rotating: piece {exiting.uuid[:8]} exited without classification"
                )

        piece_at_class = self.carousel.getPieceAtClassification()
        if piece_at_class is not None:
            self.logger.info(
                f"Rotating: piece {piece_at_class.uuid[:8]} at classification position"
            )
            return ClassificationState.SNAPPING
        else:
            self.logger.info("Rotating: no piece at classification, returning to idle")
            self.shared.classification_ready = True
            return ClassificationState.IDLE

    def cleanup(self) -> None:
        super().cleanup()
        self.start_time = None
        self.command_sent = False
