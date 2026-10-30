import time
from gpiozero import Motor, RotaryEncoder

motor_a = Motor(12, 18)
motor_b = Motor(19, 13)

encoder_a = RotaryEncoder(23, 24, max_steps=0)
encoder_b = RotaryEncoder(6, 5, max_steps=0)

last_a = encoder_a.steps
last_b = encoder_b.steps

motor_a.forward(0.5)
motor_b.forward(0.5)

try:
    while True:
        time.sleep(1)

        current_a = encoder_a.steps
        current_b = encoder_b.steps

        speed_a = current_a - last_a
        speed_b = -(current_b - last_b)

        print("Motor A:", speed_a, "steps/s")
        print("Motor B:", speed_b, "steps/s")
        print()

        last_a = current_a
        last_b = current_b

finally:
    motor_a.stop()
    motor_b.stop()