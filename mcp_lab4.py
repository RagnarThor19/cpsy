# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time
import board
import busio
import digitalio

import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn


# Create the SPI bus
spi = busio.SPI(
    clock=board.SCK,
    MISO=board.MISO,
    MOSI=board.MOSI
)

# Create the chip select
cs = digitalio.DigitalInOut(board.D5)

# Create the MCP3008 object
mcp = MCP.MCP3008(spi, cs)

# Read analog input channel 0
chan = AnalogIn(mcp, MCP.P0)


while True:
    print("Raw ADC Value:", chan.value)
    print("ADC Voltage:", chan.voltage, "V")
    print()

    time.sleep(1)