from typing import Optional, TYPE_CHECKING
from states.base_state import BaseState
from subsystems.shared_variables import SharedVariables
from .states import ClassificationState
from .carousel import Carousel
from irl.config import IRLInterface
from global_config import GlobalConfig
from vision.utils import masksOverlap

if TYPE_CHECKING:
    from vision import VisionManager

OBJECT_CLASS_ID = 0
CAROUSEL_CLASS_ID = 1


class Detecting(BaseState):
    def __init__(
        self,
        irl: IRLInterface,
        gc: GlobalConfig,
        shared: SharedVariables,
        carousel: Carousel,
        vision: "VisionManager",
    ):
        super().__init__(irl, gc)
        self.shared = shared
        self.carousel = carousel
        self.vision = vision

    def step(self) -> Optional[ClassificationState]:
        masks_by_class = self.vision.getFeederMasksByClass()
        object_masks = masks_by_class.get(OBJECT_CLASS_ID, [])
        carousel_masks = masks_by_class.get(CAROUSEL_CLASS_ID, [])

        if not object_masks or not carousel_masks:
            return None

        for obj_mask in object_masks:
            for carousel_mask in carousel_masks:
                if masksOverlap(obj_mask, carousel_mask):
                    self.logger.info("Detecting: object mask overlaps carousel")
                    self.shared.classification_ready = False
                    self.carousel.addPieceAtFeeder()
                    return ClassificationState.ROTATING

        return None

    def cleanup(self) -> None:
        super().cleanup()
