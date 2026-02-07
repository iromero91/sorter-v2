import time
import queue
from typing import Optional
from states.base_state import BaseState
from subsystems.shared_variables import SharedVariables
from .states import DistributionState
from irl.config import IRLInterface
from global_config import GlobalConfig
from sorting_profile import SortingProfile
from defs.events import KnownObjectEvent, KnownObjectData, KnownObjectStatus

SEND_DURATION_MS = 500


class Sending(BaseState):
    def __init__(
        self,
        irl: IRLInterface,
        gc: GlobalConfig,
        shared: SharedVariables,
        sorting_profile: SortingProfile,
        event_queue: queue.Queue,
    ):
        super().__init__(irl, gc)
        self.shared = shared
        self.sorting_profile = sorting_profile
        self.event_queue = event_queue
        self.sequence_complete = False

    def _emitObjectEvent(self, obj) -> None:
        event = KnownObjectEvent(
            tag="known_object",
            data=KnownObjectData(
                uuid=obj.uuid,
                created_at=obj.created_at,
                updated_at=obj.updated_at,
                status=KnownObjectStatus(obj.status),
                part_id=obj.part_id,
                category_id=obj.category_id,
                confidence=obj.confidence,
                destination_bin=obj.destination_bin,
                thumbnail=obj.thumbnail,
                top_image=obj.top_image,
                bottom_image=obj.bottom_image,
            ),
        )
        self.event_queue.put(event)

    def step(self) -> Optional[DistributionState]:
        self._ensureExecutionThreadStarted()
        if self.sequence_complete:
            piece = self.shared.pending_piece
            if piece:
                piece.status = "distributed"
                piece.updated_at = time.time()
                self._emitObjectEvent(piece)
            self.shared.distribution_ready = True
            return DistributionState.IDLE
        return None

    def cleanup(self) -> None:
        super().cleanup()
        self.sequence_complete = False

    def _executionLoop(self) -> None:
        self.logger.info("Distribution: sending piece to bin")
        time.sleep(SEND_DURATION_MS / 1000.0)
        if self._stop_event.is_set():
            return
        self.logger.info("Distribution: piece sent")
        self.sequence_complete = True
