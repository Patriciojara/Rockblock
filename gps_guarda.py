
import csv
import time
from datetime import datetime
import os

# GPS
from time import sleep
import sys
import qwiic_titan_gps

# RTC
import board
import adafruit_ds3231
# Nombre del archivo donde guardarás los datos
name = "gps_guarda"

# Encabezados del CSV
HEADERS = ["Date_TRC", "Date_GPS", "Latitud", "Longitud"]
i=1
# Si el archivo no existe, se crea con los encabezados
def generar_nombre_archivo(base_name):
    contador = 1
    while True:
        filename = f"{base_name}_{contador}.csv"
        if not os.path.exists(filename):
            return filename
        contador += 1

# --- CREAR NUEVO ARCHIVO CON HEADERS ---
FILENAME = generar_nombre_archivo(name)
print(f"Creando archivo: {FILENAME}")

with open(FILENAME, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(HEADERS)


# Inicia al GPS

print("SparkFun GPS Breakout - XA1110!")
qwiicGPS = qwiic_titan_gps.QwiicTitanGps()

if qwiicGPS.connected is False:
    print("Could not connect to to the SparkFun GPS Unit. Double check that\
            it's wired correctly.", file=sys.stderr)
    

qwiicGPS.begin()

# Inicia RTC
i2c = board.I2C()  # uses board.SCL and board.SDA
# i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
rtc = adafruit_ds3231.DS3231(i2c)
days = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")


# Bucle principal
while True:
    # Simulación de lectura de datos del sensor (reemplaza por tus lecturas reales)

    # Tiempo del rtc

    # Guardar en el CSV
    with open(FILENAME, "a", newline="") as file:

        if qwiicGPS.get_nmea_data() is True:
                Data = str(1)
                Latitud = qwiicGPS.gnss_messages['Latitude'],
                Longitud = qwiicGPS.gnss_messages['Longitude'],
                Hora_gps = qwiicGPS.gnss_messages['Time'] # Time will be UTC time as a list [hh, mm, ss]
                t = rtc.datetime
                Hora_RTC =f"{days[int(t.tm_wday)]} {t.tm_mday}/{t.tm_mon}/{t.tm_year} {t.tm_hour}:{t.tm_min:02}:{t.tm_sec:02}"
                writer = csv.writer(file)
                writer.writerow([Hora_RTC, Hora_gps, Latitud, Longitud])
                print(f"{Hora_RTC}, {Hora_gps}, {Latitud}, {Longitud}")
                sleep(1)
        else:
                Data = "0"
       
                t = rtc.datetime
                Hora_RTC =f"{days[int(t.tm_wday)]} {t.tm_mday}/{t.tm_mon}/{t.tm_year} {t.tm_hour}:{t.tm_min:02}:{t.tm_sec:02}"
                #writer = csv.writer(file)
                #writer.writerow([Hora_RTC, 0, 0, 0, Data])
                print(f"{Hora_RTC}, Error de lectura GPS")
                sleep(1)








    # Espera 1 segundo antes de la próxima lectura








# RTC


import time

import board

import adafruit_ds3231

i2c = board.I2C()  # uses board.SCL and board.SDA
# i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
rtc = adafruit_ds3231.DS3231(i2c)

# Lookup table for names of days (nicer printing).
days = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")


if False:  # change to True if you want to set the time!
    #                     year, mon, date, hour, min, sec, wday, yday, isdst
    t = time.struct_time((2017, 10, 29, 15, 14, 15, 0, -1, -1))
    # you must set year, mon, date, hour, min, sec and weekday
    # yearday is not supported, isdst can be set but we don't do anything with it at this time
    print("Setting time to:", t)  # uncomment for debugging
    rtc.datetime = t
    print()

# Main loop:
while True:
    t = rtc.datetime
    # print(t)     # uncomment for debugging
    print(f"The date is {days[int(t.tm_wday)]} {t.tm_mday}/{t.tm_mon}/{t.tm_year}")
    print(f"The time is {t.tm_hour}:{t.tm_min:02}:{t.tm_sec:02}")
    time.sleep(1)  # wait a second



