import time
from typing import Optional
from states.base_state import BaseState
from subsystems.shared_variables import SharedVariables
from .states import (
    FeederState,
    OBJECT_CLASS_ID,
    CAROUSEL_CLASS_ID,
    THIRD_V_CHANNEL_CLASS_ID,
)
from irl.config import IRLInterface
from global_config import GlobalConfig
from vision.vision_manager import VisionManager
from vision.utils import masksOverlap


class V3Dispensing(BaseState):
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

        carousel_mask = carousel_masks[0] if carousel_masks else None
        third_v_mask = third_v_masks[0] if third_v_masks else None

        for obj_mask in object_masks:
            on_carousel = carousel_mask is not None and masksOverlap(
                obj_mask, carousel_mask
            )
            on_v3 = third_v_mask is not None and masksOverlap(obj_mask, third_v_mask)

            if on_carousel:
                self.shared.classification_ready = False
                return FeederState.IDLE
            if on_v3:
                return None  # still on V3, keep pulsing

        # no piece on V3 or carousel, go back to IDLE
        return FeederState.IDLE

    def cleanup(self) -> None:
        super().cleanup()
        self.irl.third_v_channel_dc_motor.backstop(self.feeder_config.v3_pulse_speed)

    def _executionLoop(self) -> None:
        motor = self.irl.third_v_channel_dc_motor
        pulse_ms = self.feeder_config.v3_pulse_length_ms
        pause_ms = self.feeder_config.pause_ms
        speed = self.feeder_config.v3_pulse_speed

        while not self._stop_event.is_set():
            motor.setSpeed(speed)
            time.sleep(pulse_ms / 1000.0)
            motor.backstop(speed)
            time.sleep(pause_ms / 1000.0)
