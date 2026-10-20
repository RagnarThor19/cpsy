import time

from gpiozero import Motor, RotaryEncoder, Button
from simple_pid import PID

import board
import busio
import digitalio
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

# motor setup

motor_a = Motor(12, 18)
motor_b = Motor(19, 13)

encoder_a = RotaryEncoder(23, 24, max_steps=0)
encoder_b = RotaryEncoder(6, 5, max_steps=0)

# emergency stop

emergency = Button(
    26,
    pull_up=True,
    bounce_time=0.05
)

# IR SENSOR / MCP3008

spi = busio.SPI(
    clock=board.SCK,
    MISO=board.MISO,
    MOSI=board.MOSI
)

cs = digitalio.DigitalInOut(board.CE0)

mcp = MCP.MCP3008(spi, cs)

# J14 IR is connected to MCP3008 CH0
ir = AnalogIn(mcp, MCP.P0)

#encoder calibration

STEPS_PER_REV_A = 626.5
STEPS_PER_REV_B = 655.4

# PID settings

TARGET_SPEED = 0.038  # rotations per second

BASE_POWER_A = 0.47
BASE_POWER_B = 0.53

KP = 4.0
KI = 0
KD = 0

pid_a = PID(KP, KI, KD, setpoint=TARGET_SPEED)
pid_b = PID(KP, KI, KD, setpoint=TARGET_SPEED)

pid_a.output_limits = (-0.25, 0.25)
pid_b.output_limits = (-0.25, 0.25)

# collision settings

IR_STOP_VOLTAGE = 1.60
IR_CHECKS_PER_SECOND = 50  # IR is checked every 1/50 = 0.02 s

# functions
def stop_robot():
    motor_a.stop()
    motor_b.stop()


def read_ir_voltage():
    return ir.voltage


# emergency button immediately stops motors
emergency.when_pressed = stop_robot


# main program
last_a = encoder_a.steps
last_b = encoder_b.steps

power_a = BASE_POWER_A
power_b = BASE_POWER_B

try:
    motor_a.forward(power_a)
    motor_b.forward(power_b)

    while True:

        # wait about 1 second, but check the IR sensor many times while waiting
        obstacle = False
        emergency_stop = False

        for _ in range(IR_CHECKS_PER_SECOND):
            time.sleep(1 / IR_CHECKS_PER_SECOND)

            if emergency.is_pressed:
                emergency_stop = True
                break

            voltage = read_ir_voltage()

            if voltage >= IR_STOP_VOLTAGE:
                obstacle = True
                break

        if emergency_stop:
            stop_robot()
            print("EMERGENCY STOP!!!!!!!!!")
            break

        if obstacle:
            stop_robot()
            print("OBSTACLE DETECTED - STOP THE MFKN CAR! | IR:", round(voltage, 2), "V")
            break

        current_a = encoder_a.steps
        current_b = encoder_b.steps

        steps_a = current_a - last_a
        steps_b = -(current_b - last_b)

        last_a = current_a
        last_b = current_b

        # convert encoder counts to wheel rotations/second
        speed_a = steps_a / STEPS_PER_REV_A
        speed_b = steps_b / STEPS_PER_REV_B

        # PID corrections
        correction_a = pid_a(speed_a)
        correction_b = pid_b(speed_b)

        power_a = BASE_POWER_A + correction_a
        power_b = BASE_POWER_B + correction_b

        power_a = max(0, min(1, power_a))
        power_b = max(0, min(1, power_b))

        motor_a.forward(power_a)
        motor_b.forward(power_b)

        print(
            "A:", round(speed_a, 4),
            "rev/s power:", round(power_a, 2),
            "| B:", round(speed_b, 4),
            "rev/s power:", round(power_b, 2),
            "| IR:", round(voltage, 2), "V"
        )

finally:
    stop_robot()

    emergency.close()
    encoder_a.close()
    encoder_b.close()