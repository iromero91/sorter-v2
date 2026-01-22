from typing import Optional, Dict, List
import time
import logging
from .known_object import KnownObject

NUM_PLATFORMS = 4
FEEDER_POSITION = 0
CLASSIFICATION_POSITION = 1
INTERMEDIATE_POSITION = 2
EXIT_POSITION = 3


class Carousel:
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.platforms: List[Optional[KnownObject]] = [None] * NUM_PLATFORMS
        self.pending_classifications: Dict[str, KnownObject] = {}
        self.logger = logger

    def _log(self, msg: str) -> None:
        if self.logger:
            self.logger.info(f"Carousel: {msg}")

    def _platformSummary(self) -> str:
        return (
            "[" + ", ".join(p.uuid[:8] if p else "empty" for p in self.platforms) + "]"
        )

    def addPieceAtFeeder(self) -> KnownObject:
        obj = KnownObject()
        self.platforms[FEEDER_POSITION] = obj
        self._log(f"added piece {obj.uuid[:8]} at feeder -> {self._platformSummary()}")
        return obj

    def rotate(self) -> Optional[KnownObject]:
        exiting = self.platforms[EXIT_POSITION]
        self.platforms = [None] + self.platforms[: NUM_PLATFORMS - 1]
        exit_str = exiting.uuid[:8] if exiting else "none"
        self._log(f"rotated, exiting={exit_str} -> {self._platformSummary()}")
        return exiting

    def getPieceAtClassification(self) -> Optional[KnownObject]:
        return self.platforms[CLASSIFICATION_POSITION]

    def getPieceAtIntermediate(self) -> Optional[KnownObject]:
        return self.platforms[INTERMEDIATE_POSITION]

    def getPieceAtExit(self) -> Optional[KnownObject]:
        return self.platforms[EXIT_POSITION]

    def markPendingClassification(self, obj: KnownObject) -> None:
        self.pending_classifications[obj.uuid] = obj
        self._log(
            f"marked {obj.uuid[:8]} pending, {len(self.pending_classifications)} in flight"
        )

    def resolveClassification(self, uuid: str, part_id: str) -> None:
        if uuid in self.pending_classifications:
            obj = self.pending_classifications[uuid]
            obj.part_id = part_id
            obj.updated_at = time.time()
            del self.pending_classifications[uuid]
            self._log(
                f"resolved {uuid[:8]} -> {part_id}, {len(self.pending_classifications)} in flight"
            )

    def hasPieceAtFeeder(self) -> bool:
        return self.platforms[FEEDER_POSITION] is not None

    def exitPieceReady(self) -> bool:
        piece = self.platforms[EXIT_POSITION]
        return piece is not None and piece.part_id is not None
