from typing import TYPE_CHECKING
from global_config import GlobalConfig
from blob_manager import getStepperPosition, setStepperPosition

if TYPE_CHECKING:
    from .mcu import MCU

STEPS_PER_REV = 200
DEFAULT_MICROSTEPPING = 8  # 1600 steps/rev total
BASE_DELAY_US = 400


class Stepper:
    def __init__(
        self,
        gc: GlobalConfig,
        mcu: "MCU",
        step_pin: int,
        dir_pin: int,
        enable_pin: int,
        name: str,
        steps_per_rev: int = STEPS_PER_REV,
        microstepping: int = DEFAULT_MICROSTEPPING,
        default_delay_us: int = BASE_DELAY_US,
    ):
        self.gc = gc
        self.mcu = mcu
        self.step_pin = step_pin
        self.dir_pin = dir_pin
        self.enable_pin = enable_pin
        self.name = name
        self.steps_per_rev = steps_per_rev
        self.microstepping = microstepping
        self.default_delay_us = default_delay_us
        self.total_steps_per_rev = steps_per_rev * microstepping
        self.current_position_steps = getStepperPosition(name)

        logger = gc.logger
        logger.info(
            f"Initialized Stepper '{name}' with step={step_pin}, dir={dir_pin}, enable={enable_pin}, position={self.current_position_steps}"
        )

        mcu.command("P", step_pin, 1)
        mcu.command("P", dir_pin, 1)
        mcu.command("P", enable_pin, 1)
        mcu.command("D", enable_pin, 0)

    def rotate(self, deg: float, delay_us: int | None = None) -> None:
        if delay_us is None:
            delay_us = self.default_delay_us
        steps = int((deg / 360.0) * self.total_steps_per_rev)
        self.gc.logger.info(
            f"Stepper '{self.name}' rotating {deg}° ({steps} steps, delay={delay_us}us)"
        )
        self.mcu.command("T", self.step_pin, self.dir_pin, steps, delay_us)
        self.current_position_steps += steps
        setStepperPosition(self.name, self.current_position_steps)

    def moveSteps(self, steps: int, delay_us: int | None = None) -> None:
        if delay_us is None:
            delay_us = self.default_delay_us
        self.mcu.command("T", self.step_pin, self.dir_pin, steps, delay_us)
        self.current_position_steps += steps
        setStepperPosition(self.name, self.current_position_steps)

    def disable(self) -> None:
        self.mcu.command("D", self.enable_pin, 1)
