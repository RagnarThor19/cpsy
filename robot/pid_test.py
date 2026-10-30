import time

from gpiozero import Motor, RotaryEncoder
from simple_pid import PID

# Motors
motor_a = Motor(12, 18)
motor_b = Motor(19, 13)

# Encoders
encoder_a = RotaryEncoder(23, 24, max_steps=0)
encoder_b = RotaryEncoder(6, 5, max_steps=0)

#average encoder counts measured for one full wheel rotation
STEPS_PER_REV_A = 626.5
STEPS_PER_REV_B = 655.4

#target physical wheel speed in rotations per second
TARGET_SPEED = 0.038

# Baseline powers from our straight-driving test
BASE_POWER_A = 0.47
BASE_POWER_B = 0.53

# start with proportional control only
# new Kp because our units are now rotations/s instead of steps/s
pid_a = PID(4.0, 0, 0, setpoint=TARGET_SPEED)
pid_b = PID(4.0, 0, 0, setpoint=TARGET_SPEED)

# dont let PID make massive corrections
pid_a.output_limits = (-0.25, 0.25)
pid_b.output_limits = (-0.25, 0.25)

last_a = encoder_a.steps
last_b = encoder_b.steps

power_a = BASE_POWER_A
power_b = BASE_POWER_B

motor_a.forward(power_a)
motor_b.forward(power_b)


try:
    while True:
        time.sleep(1)

        current_a = encoder_a.steps
        current_b = encoder_b.steps

        # encoder steps during the last 1 seconds
        steps_a = current_a - last_a
        steps_b = -(current_b - last_b)

        last_a = current_a
        last_b = current_b

        # divide by steps/revolution to revolutions/second
        speed_a = steps_a / STEPS_PER_REV_A
        speed_b = steps_b / STEPS_PER_REV_B

        # pid correction
        correction_a = pid_a(speed_a)
        correction_b = pid_b(speed_b)

        power_a = BASE_POWER_A + correction_a
        power_b = BASE_POWER_B + correction_b

        # keep motor power valid
        power_a = max(0, min(1, power_a))
        power_b = max(0, min(1, power_b))
        motor_a.forward(power_a)
        motor_b.forward(power_b)

        print(
            "A:", round(speed_a, 4),
            "rev/s power:", round(power_a, 2),
            "| B:", round(speed_b, 4),
            "rev/s power:", round(power_b, 2)
        )

finally:
    motor_a.stop()
    motor_b.stop()