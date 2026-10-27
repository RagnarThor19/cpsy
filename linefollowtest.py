import time
from threading import Event

from gpiozero import Motor, Button

import board
import busio
import digitalio
import adafruit_tcs34725
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn


# motor setup
motor_a = Motor(12, 18)
motor_b = Motor(19, 13)


#emergency button
emergency = Button(
    26,
    pull_up=True,
    bounce_time=0.05
)

emergency_stop = Event()


# colour sensor setup
i2c = board.I2C()
color_sensor = adafruit_tcs34725.TCS34725(i2c)

BLACK_THRESHOLD = 40


# IR sensor setup
spi = busio.SPI(
    clock=board.SCK,
    MISO=board.MISO,
    MOSI=board.MOSI
)

cs = digitalio.DigitalInOut(board.CE0)
mcp = MCP.MCP3008(spi, cs)

ir = AnalogIn(mcp, MCP.P0)

IR_STOP_VOLTAGE = 1.90


# movement settings
POWER = 0.8

MOVE_TIME = 0.009
PAUSE_TIME = 0.06

MAX_WHITE_STEPS = 50


# functions
def stop_robot():
    motor_a.stop()
    motor_b.stop()


def emergency_pressed():
    emergency_stop.set()
    stop_robot()


def left_step():
    motor_a.stop()
    motor_b.forward(POWER)

    time.sleep(MOVE_TIME)

    stop_robot()
    time.sleep(PAUSE_TIME)


def right_step():
    motor_a.forward(POWER)
    motor_b.stop()

    time.sleep(MOVE_TIME)

    stop_robot()
    time.sleep(PAUSE_TIME)


def read_clear():
    r, g, b, clear = color_sensor.color_raw
    return clear


def read_ir_voltage():
    return ir.voltage


# emergency stop
emergency.when_pressed = emergency_pressed


# starting state
direction = "left"
was_on_line = True
white_steps = 0


# main program
try:
    while True:

        # emergency check
        if emergency_stop.is_set():
            print("EMERGENCY STOP!!!! CHECK FOR FIRES !!!! ")
            break

        # obstacle check
        voltage = read_ir_voltage()

        if voltage >= IR_STOP_VOLTAGE:
            print("OBSTACLE IN THE WAY STOP THE ROBOT!!!!!!!!")
            break

        # read colour sensor
        clear = read_clear()
        on_line = clear < BLACK_THRESHOLD

        # switch direction when leaving black
        if was_on_line and not on_line:

            if direction == "left":
                direction = "right"
            else:
                direction = "left"

            print("Edge found, switching to", direction)

            white_steps = 0

        # count white readings
        if on_line:
            white_steps = 0
        else:
            white_steps += 1

        # stop if line is completely lost
        if white_steps >= MAX_WHITE_STEPS:
            print("LINE LOST, STOP. ITS A FAILURE :( ")
            break

        was_on_line = on_line

        print(
            "Clear:", clear,
            "| Direction:", direction,
            "| IR:", round(voltage, 2)
        )

        # one tiny movement
        if direction == "left":
            left_step()
        else:
            right_step()


finally:
    stop_robot()
    emergency.close()

    print("Robot stopped")