# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time

import board

import adafruit_icm20x

i2c = board.I2C()  # uses board.SCL and board.SDA
# i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
imu = adafruit_icm20x.ICM20948(i2c, address=0x68) #creates imu object, for me the adress was 0x68 and not specifying the address caused issues

while True:
    print("Acceleration: X:{:.2f}, Y: {:.2f}, Z: {:.2f} m/s^2".format(*imu.acceleration)) #prints a clear formatted version of the acceleration readings
    print("Gyro X:{:.2f}, Y: {:.2f}, Z: {:.2f} rads/s".format(*imu.gyro)) #prints a clear formatted version of the gyro readings
    print("Magnetometer X:{:.2f}, Y: {:.2f}, Z: {:.2f} uT".format(*imu.magnetic)) #prints a clear formatted version of the magnetic readings
    print("") #just for distinction for different readings
    time.sleep(1) #breaks the program for 1 sec
