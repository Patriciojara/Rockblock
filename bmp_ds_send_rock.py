# Autor: Patricio Jara Quiroz
# Fecha: 08-10-2025
# Descripción: lee bmp y rtc y envia por rockblock




# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# Simple demo of reading and writing the time for the DS3231 real-time clock.
# Change the if False to if True below to set the time, otherwise it will just
# print the current date and time every second.  Notice also comments to adjust
# for working with hardware vs. software I2C.

import time

import board

import adafruit_ds3231

import time
import board
import busio
from adafruit_bme280.advanced import Adafruit_BME280_I2C



from time import sleep
import sys
import qwiic_titan_gps


i2c_ds3231 = board.I2C()  # uses board.SCL and board.SDA ds3231
# i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
rtc = adafruit_ds3231.DS3231(i2c_ds3231)

# Lookup table for names of days (nicer printing).
days = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")


# Inicializa el bus I2C
i2c_bmp = busio.I2C(board.SCL, board.SDA)

# Crea el objeto del sensor en la dirección 0x76
bme280 = Adafruit_BME280_I2C(i2c_bmp, address=0x76)

# Establece la presión a nivel del mar (opcional, para altitud)
bme280.sea_level_pressure = 1013.25


# Inicializa el GPS Qwiic Titan

qwiicGPS = qwiic_titan_gps.QwiicTitanGps()

if qwiicGPS.connected is False:
    print("Could not connect to to the SparkFun GPS Unit. Double check that\
            it's wired correctly.", file=sys.stderr)
   

qwiicGPS.begin()


# Main loop:
while True:
    t = rtc.datetime
    # print(t)     # uncomment for debugging
    print(
        f"RTC:{days[int(t.tm_wday)]} {t.tm_mday}/{t.tm_mon}/{t.tm_year}/ "
        f"{t.tm_hour}:{t.tm_min:02}:{t.tm_sec:02}//"
        f"BMP: T: {bme280.temperature:.2f} °C, P: {bme280.pressure:.2f} hPa, "
        f"H: {bme280.humidity:.2f} %, A: {bme280.altitude:.2f} m //"
        #f"GPS: La: -{qwiicGPS.gnss_messages['Latitude']}, Lo: -{qwiicGPS.gnss_messages['Longitude']} "
    )
    time.sleep(1)  # wait a second






