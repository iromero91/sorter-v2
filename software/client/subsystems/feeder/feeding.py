import time
from typing import Optional
from states.base_state import BaseState
from subsystems.shared_variables import SharedVariables
from .states import FeederState
from .analysis import FeederAnalysisState, analyzeFeederState
from irl.config import IRLInterface, IRLConfig
from global_config import GlobalConfig
from vision import VisionManager
from defs.consts import FEEDER_OBJECT_CLASS_ID, FEEDER_CAROUSEL_CLASS_ID


class Feeding(BaseState):
    def __init__(
        self,
        irl: IRLInterface,
        irl_config: IRLConfig,
        gc: GlobalConfig,
        shared: SharedVariables,
        vision: VisionManager,
    ):
        super().__init__(irl, gc)
        self.irl_config = irl_config
        self.shared = shared
        self.vision = vision

    def step(self) -> Optional[FeederState]:
        self._ensureExecutionThreadStarted()

        if not self.shared.classification_ready:
            return FeederState.IDLE
        return None

    def _executionLoop(self) -> None:
        fc = self.gc.feeder_config
        irl_cfg = self.irl_config

        while not self._stop_event.is_set():
            # get vision data
            masks_by_class = self.vision.getFeederMasksByClass()
            object_detected_masks = masks_by_class.get(FEEDER_OBJECT_CLASS_ID, [])
            carousel_detected_masks = masks_by_class.get(FEEDER_CAROUSEL_CLASS_ID, [])
            carousel_detected_mask = (
                carousel_detected_masks[0] if carousel_detected_masks else None
            )

            channels = self.vision.getIdentifiedChannels(
                irl_cfg.first_c_channel_aruco_tag_id,
                irl_cfg.second_c_channel_aruco_tag_id,
                irl_cfg.third_c_channel_aruco_tag_id,
            )

            # print('~~~identified channels', channels.second_channel_mask.instance_id, channels.third_channel_mask.instance_id)

            # count objects on each channel for debug
            objects_on_2 = 0
            objects_on_3 = 0
            objects_on_neither = 0
            for obj_dm in object_detected_masks:
                from .analysis import determineObjectChannel

                channel_id = determineObjectChannel(
                    obj_dm, channels, fc.object_channel_overlap_threshold
                )
                if channel_id == 2:
                    objects_on_2 += 1
                elif channel_id == 3:
                    objects_on_3 += 1
                else:
                    objects_on_neither += 1

            self.gc.logger.info(
                f"Objects on channels - 2nd: {objects_on_2}, 3rd: {objects_on_3}, neither: {objects_on_neither}, total: {len(object_detected_masks)}"
            )

            # analyze state
            state = analyzeFeederState(
                object_detected_masks, channels, carousel_detected_mask, fc
            )
            ACTUALLY_RUN = True

            # act based on state
            if state == FeederAnalysisState.OBJECT_ABOUT_TO_FALL:
                self.gc.logger.info(
                    "Feeder: object about to fall, pulsing 3rd (precise)"
                )
                cfg = fc.third_rotor_precision
                if ACTUALLY_RUN:
                    self.irl.third_c_channel_rotor_stepper.moveSteps(
                        -cfg.steps_per_pulse, cfg.delay_us
                    )
                if cfg.delay_between_pulse_ms > 0:
                    time.sleep(cfg.delay_between_pulse_ms / 1000.0)
            elif state == FeederAnalysisState.OBJECT_IN_3_2_DROPZONE:
                self.gc.logger.info("Feeder: object in 3-2 dropzone, pulsing 3rd")
                cfg = fc.third_rotor_normal
                if ACTUALLY_RUN:
                    self.irl.third_c_channel_rotor_stepper.moveSteps(
                        -cfg.steps_per_pulse, cfg.delay_us
                    )
                if cfg.delay_between_pulse_ms > 0:
                    time.sleep(cfg.delay_between_pulse_ms / 1000.0)
            elif state == FeederAnalysisState.OBJECT_IN_2_1_DROPZONE:
                self.gc.logger.info("Feeder: object in 2-1 dropzone, pulsing 2nd")
                cfg = fc.second_rotor
                if ACTUALLY_RUN:
                    self.irl.second_c_channel_rotor_stepper.moveSteps(
                        -cfg.steps_per_pulse, cfg.delay_us
                    )
                if cfg.delay_between_pulse_ms > 0:
                    time.sleep(cfg.delay_between_pulse_ms / 1000.0)
            else:
                self.gc.logger.info("Feeder: clear, pulsing 1st")
                cfg = fc.first_rotor
                if ACTUALLY_RUN:
                    self.irl.first_c_channel_rotor_stepper.moveSteps(
                        -cfg.steps_per_pulse, cfg.delay_us
                    )
                if cfg.delay_between_pulse_ms > 0:
                    time.sleep(cfg.delay_between_pulse_ms / 1000.0)

    def cleanup(self) -> None:
        super().cleanup()
