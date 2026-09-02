# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time
import math
import board
import adafruit_icm20x
from gpiozero import LED


i2c = board.I2C()

# My imu is at address 0x68
imu = adafruit_icm20x.ICM20948(i2c, address=0x68)

# LEDs
red_led = LED(17)      #physical pin 11
green_led = LED(27)    #physical pin 13

# Found from magnetometer calibration using the  adafruit code and finding the max and min i got
# the readings were off so i have to use this because there were "hard iron offset"
# you can read about it on the magnetometer calibration in adafruits website, its weird.
X_OFFSET = -39.225
Y_OFFSET = -9.975

# Basically just how close x and y need to be to 0 for it to count as level
LEVEL_THRESHOLD = 1.0

# the hardware is not very accurate so ill read within 20 degrees of 360 (340-20 degrees means north)
NORTH_THRESHOLD = 20

while True:

    # I split the code from adafruit into 3 variables so i can use specific ones for checking level (x & y used)
    ax, ay, az = imu.acceleration

    # Read magnetometer values, same as above.
    mx, my, mz = imu.magnetic


    # just checking if its level, if it is then turn green led on, if not turn it off
    if abs(ax) < LEVEL_THRESHOLD and abs(ay) < LEVEL_THRESHOLD:
        green_led.on()
        level = True
    else:
        green_led.off()
        level = False


    # same as above but now just checking if we face north
    # Remove the offsets found during calibration
    mx = mx - X_OFFSET
    my = my - Y_OFFSET


    # atan2 formula is used to calculate where we are facing
    heading = math.degrees(math.atan2(my, mx))

    # Convert negative angles to 0-360 degrees
    if heading < 0:
        heading += 360

    # North is around 0 degrees.
    # 340-360 and 0-20 are both close to North.
    if heading >= 360 - NORTH_THRESHOLD or heading <= NORTH_THRESHOLD:
        red_led.on()
        north = True
    else:
        red_led.off()
        north = False


    # printing section, basically as from adafruit code but just added level and north

    print(
        "Acceleration: X:{:.2f}, Y:{:.2f}, Z:{:.2f} m/s^2"
        .format(ax, ay, az)
    )

    print(
        "Gyro X:{:.2f}, Y:{:.2f}, Z:{:.2f} rads/s"
        .format(*imu.gyro)
    )

    print(
        "Magnetometer corrected X:{:.2f}, Y:{:.2f}, Z:{:.2f} uT"
        .format(mx, my, mz)
    )

    print("Heading: {:.2f} degrees".format(heading))
    print("Level:", level)
    print("North:", north)
    print("")
    time.sleep(1)