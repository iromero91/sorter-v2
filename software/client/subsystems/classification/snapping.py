from typing import Optional, TYPE_CHECKING
import os
import time
import cv2
from states.base_state import BaseState
from subsystems.shared_variables import SharedVariables
from .states import ClassificationState
from .carousel import Carousel
from irl.config import IRLInterface
from global_config import GlobalConfig

if TYPE_CHECKING:
    from vision import VisionManager
    from classification import BrickognizeClient

SNAP_DIR = "/tmp/sorter_snaps"
SNAP_DELAY_MS = 200


class Snapping(BaseState):
    def __init__(
        self,
        irl: IRLInterface,
        gc: GlobalConfig,
        shared: SharedVariables,
        carousel: Carousel,
        vision: "VisionManager",
        brickognize: "BrickognizeClient",
    ):
        super().__init__(irl, gc)
        self.shared = shared
        self.carousel = carousel
        self.vision = vision
        self.brickognize = brickognize
        self.start_time: Optional[float] = None
        self.snapped = False

    def step(self) -> Optional[ClassificationState]:
        if self.start_time is None:
            self.start_time = time.time()
            self.logger.info("Snapping: waiting for camera settle")
            return None

        elapsed_ms = (time.time() - self.start_time) * 1000
        if elapsed_ms < SNAP_DELAY_MS:
            return None

        if not self.snapped:
            self._captureAndClassify()
            self.snapped = True

        self.shared.classification_ready = True
        return ClassificationState.IDLE

    def _captureAndClassify(self) -> None:
        piece = self.carousel.getPieceAtClassification()
        if piece is None:
            self.logger.warn("Snapping: no piece at classification position")
            return

        top_frame, bottom_frame = self.vision.captureFreshClassificationFrames()
        if top_frame is None or bottom_frame is None:
            self.logger.warn("Snapping: camera frames not available")
            return

        os.makedirs(SNAP_DIR, exist_ok=True)
        top_path = os.path.join(SNAP_DIR, f"{piece.uuid}_top.jpg")
        bottom_path = os.path.join(SNAP_DIR, f"{piece.uuid}_bottom.jpg")
        cv2.imwrite(top_path, top_frame.raw)
        cv2.imwrite(bottom_path, bottom_frame.raw)
        self.logger.info(f"Snapping: saved {piece.uuid[:8]} to {SNAP_DIR}")

        self.carousel.markPendingClassification(piece)

        def onResult(part_id: Optional[str]) -> None:
            self.carousel.resolveClassification(piece.uuid, part_id or "unknown")
            self.logger.info(f"Snapping: classified {piece.uuid[:8]} -> {part_id}")

        self.brickognize.classify(top_frame.raw, bottom_frame.raw, onResult)

    def cleanup(self) -> None:
        super().cleanup()
        self.start_time = None
        self.snapped = False
