import time

from gpiozero import Motor, RotaryEncoder
from simple_pid import PID

# Motors
motor_a = Motor(12, 18)
motor_b = Motor(19, 13)

# Encoders
encoder_a = RotaryEncoder(23, 24, max_steps=0)
encoder_b = RotaryEncoder(6, 5, max_steps=0)

TARGET_SPEED = 24
BASE_POWER = 0.5

# start with only proportional control
pid_a = PID(0.02, 0, 0, setpoint=TARGET_SPEED)
pid_b = PID(0.02, 0, 0, setpoint=TARGET_SPEED)

# pid only gives us a small correction
pid_a.output_limits = (-0.4, 0.4)
pid_b.output_limits = (-0.4, 0.4)

last_a = encoder_a.steps
last_b = encoder_b.steps

power_a = BASE_POWER
power_b = BASE_POWER

motor_a.forward(power_a)
motor_b.forward(power_b)

try:
    while True:
        time.sleep(0.5)

        current_a = encoder_a.steps
        current_b = encoder_b.steps

        # steps during 0.5 seconds multiply by 2 for steps/second
        speed_a = (current_a - last_a) * 2
        speed_b = -(current_b - last_b) * 2

        last_a = current_a
        last_b = current_b

        correction_a = pid_a(speed_a)
        correction_b = pid_b(speed_b)

        power_a = BASE_POWER + correction_a
        power_b = BASE_POWER + correction_b

        # motor power must stay between 0 and 1
        power_a = max(0, min(1, power_a))
        power_b = max(0, min(1, power_b))

        motor_a.forward(power_a)
        motor_b.forward(power_b)

        print(
            "A:", speed_a, "steps/s power:", round(power_a, 2),
            "| B:", speed_b, "steps/s power:", round(power_b, 2)
        )

finally:
    motor_a.stop()
    motor_b.stop()