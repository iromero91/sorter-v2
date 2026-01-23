import sys
import time
import readchar
from global_config import mkGlobalConfig
from irl.config import mkIRLConfig, mkIRLInterface


SPEED_STEP = 1
PULSE_STEP = 25


def main():
    gc = mkGlobalConfig()
    irl_config = mkIRLConfig()
    irl = mkIRLInterface(irl_config, gc)
    feeder_config = gc.feeder_config

    v1 = irl.first_v_channel_dc_motor
    v2 = irl.second_v_channel_dc_motor
    v3 = irl.third_v_channel_dc_motor

    edit_mode = False
    edit_motor = 1  # 1, 2, or 3
    edit_field = "speed"  # "speed" or "pulse"

    def printStatus():
        print("\033[2J\033[H", end="")
        print("Manual Feeder Control")
        print("=====================")
        print()
        print("Motor Settings:")
        m1 = " >> " if edit_mode and edit_motor == 1 else "    "
        m2 = " >> " if edit_mode and edit_motor == 2 else "    "
        m3 = " >> " if edit_mode and edit_motor == 3 else "    "
        s_mark = "[S]" if edit_mode and edit_field == "speed" else "   "
        p_mark = "[P]" if edit_mode and edit_field == "pulse" else "   "
        print(
            f"{m1}V1: {s_mark}speed={feeder_config.v1_pulse_speed}, {p_mark}pulse={feeder_config.v1_pulse_length_ms}ms"
        )
        print(
            f"{m2}V2: {s_mark}speed={feeder_config.v2_pulse_speed}, {p_mark}pulse={feeder_config.v2_pulse_length_ms}ms"
        )
        print(
            f"{m3}V3: {s_mark}speed={feeder_config.v3_pulse_speed}, {p_mark}pulse={feeder_config.v3_pulse_length_ms}ms"
        )
        print(f"    Pause between pulses: {feeder_config.pause_ms}ms")
        print()
        if edit_mode:
            print("Edit Mode (E to exit)")
            print("  1/2/3     Select motor")
            print("  S/P       Toggle speed/pulse")
            print("  UP/DOWN   Adjust value")
            print("  +/-       Adjust value")
        else:
            print("Controls:")
            print("  1  Pulse V1 (first v-channel)")
            print("  2  Pulse V2 (second v-channel)")
            print("  3  Pulse V3 (third v-channel)")
            print("  E  Edit mode")
            print("  Q  Quit")
        print()

    def pulse(motor, speed, pulse_ms):
        motor.setSpeed(speed)
        time.sleep(pulse_ms / 1000.0)
        motor.backstop(speed)

    def adjustValue(delta):
        nonlocal feeder_config
        if edit_field == "speed":
            step = SPEED_STEP * delta
            if edit_motor == 1:
                feeder_config.v1_pulse_speed = max(
                    -255, min(255, feeder_config.v1_pulse_speed + step)
                )
            elif edit_motor == 2:
                feeder_config.v2_pulse_speed = max(
                    -255, min(255, feeder_config.v2_pulse_speed + step)
                )
            elif edit_motor == 3:
                feeder_config.v3_pulse_speed = max(
                    -255, min(255, feeder_config.v3_pulse_speed + step)
                )
        else:
            step = PULSE_STEP * delta
            if edit_motor == 1:
                feeder_config.v1_pulse_length_ms = max(
                    0, feeder_config.v1_pulse_length_ms + step
                )
            elif edit_motor == 2:
                feeder_config.v2_pulse_length_ms = max(
                    0, feeder_config.v2_pulse_length_ms + step
                )
            elif edit_motor == 3:
                feeder_config.v3_pulse_length_ms = max(
                    0, feeder_config.v3_pulse_length_ms + step
                )

    printStatus()

    while True:
        key = readchar.readkey()

        if edit_mode:
            if key == "1":
                edit_motor = 1
            elif key == "2":
                edit_motor = 2
            elif key == "3":
                edit_motor = 3
            elif key.lower() == "s":
                edit_field = "speed"
            elif key.lower() == "p":
                edit_field = "pulse"
            elif key in ("\x1b[A", "+", "="):  # up arrow or +
                adjustValue(1)
            elif key in ("\x1b[B", "-", "_"):  # down arrow or -
                adjustValue(-1)
            elif key.lower() == "e":
                edit_mode = False
            printStatus()
        elif key == "1":
            print("Pulsing V1...")
            pulse(v1, feeder_config.v1_pulse_speed, feeder_config.v1_pulse_length_ms)
            print("Done")
        elif key == "2":
            print("Pulsing V2...")
            pulse(v2, feeder_config.v2_pulse_speed, feeder_config.v2_pulse_length_ms)
            print("Done")
        elif key == "3":
            print("Pulsing V3...")
            pulse(v3, feeder_config.v3_pulse_speed, feeder_config.v3_pulse_length_ms)
            print("Done")
        elif key.lower() == "e":
            edit_mode = True
            printStatus()
        elif key.lower() == "q":
            print("Exiting...")
            irl.shutdownMotors()
            sys.exit(0)


if __name__ == "__main__":
    main()
