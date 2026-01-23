import time
from typing import Optional
from states.base_state import BaseState
from subsystems.shared_variables import SharedVariables
from .states import (
    FeederState,
    OBJECT_CLASS_ID,
    CAROUSEL_CLASS_ID,
    THIRD_V_CHANNEL_CLASS_ID,
    SECOND_V_CHANNEL_CLASS_ID,
    FIRST_V_CHANNEL_CLASS_ID,
)
from irl.config import IRLInterface
from global_config import GlobalConfig
from vision.vision_manager import VisionManager
from vision.utils import masksOverlap, masksWithinDistance


class V1Loading(BaseState):
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
        self.feeder_config = gc.feeder_config

    def step(self) -> Optional[FeederState]:
        self._ensureExecutionThreadStarted()

        masks_by_class = self.vision.getFeederMasksByClass()
        object_masks = masks_by_class.get(OBJECT_CLASS_ID, [])
        carousel_masks = masks_by_class.get(CAROUSEL_CLASS_ID, [])
        third_v_masks = masks_by_class.get(THIRD_V_CHANNEL_CLASS_ID, [])
        second_v_masks = masks_by_class.get(SECOND_V_CHANNEL_CLASS_ID, [])
        first_v_masks = masks_by_class.get(FIRST_V_CHANNEL_CLASS_ID, [])

        threshold = self.feeder_config.proximity_threshold_px
        carousel_mask = carousel_masks[0] if carousel_masks else None
        third_v_mask = third_v_masks[0] if third_v_masks else None
        second_v_mask = second_v_masks[0] if second_v_masks else None
        first_v_mask = first_v_masks[0] if first_v_masks else None

        # check for blocking pieces
        v1_blocking_v2 = False
        v2_blocking_v3 = False
        for obj_mask in object_masks:
            on_v1 = first_v_mask is not None and masksOverlap(obj_mask, first_v_mask)
            on_v2 = second_v_mask is not None and masksOverlap(obj_mask, second_v_mask)
            near_v2 = second_v_mask is not None and masksWithinDistance(
                obj_mask, second_v_mask, threshold
            )
            near_v3 = third_v_mask is not None and masksWithinDistance(
                obj_mask, third_v_mask, threshold
            )
            if on_v1 and near_v2:
                v1_blocking_v2 = True
            if on_v2 and near_v3:
                v2_blocking_v3 = True

        for obj_mask in object_masks:
            on_carousel = carousel_mask is not None and masksOverlap(
                obj_mask, carousel_mask
            )
            on_v3 = third_v_mask is not None and masksOverlap(obj_mask, third_v_mask)
            on_v2 = second_v_mask is not None and masksOverlap(obj_mask, second_v_mask)
            on_v1 = first_v_mask is not None and masksOverlap(obj_mask, first_v_mask)

            if on_carousel:
                return (
                    FeederState.V3_DISPENSING
                    if self.shared.classification_ready
                    else FeederState.IDLE
                )
            if on_v3 and not v2_blocking_v3:
                return (
                    FeederState.V3_DISPENSING
                    if self.shared.classification_ready
                    else FeederState.IDLE
                )
            if on_v2 and not v1_blocking_v2:
                return FeederState.V2_LOADING
            if on_v1:
                return None  # stay in V1_LOADING

        return FeederState.IDLE

    def cleanup(self) -> None:
        super().cleanup()
        self.irl.first_v_channel_dc_motor.backstop(self.feeder_config.v1_pulse_speed)

    def _executionLoop(self) -> None:
        motor = self.irl.first_v_channel_dc_motor
        pulse_ms = self.feeder_config.v1_pulse_length_ms
        pause_ms = self.feeder_config.pause_ms
        speed = self.feeder_config.v1_pulse_speed

        while not self._stop_event.is_set():
            motor.setSpeed(speed)
            time.sleep(pulse_ms / 1000.0)
            motor.backstop(speed)
            time.sleep(pause_ms / 1000.0)
