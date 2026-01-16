
from time import sleep
import sys
import os
import csv
import re
import qwiic_titan_gps
import subprocess


import numpy as np
import time
import board
import busio
from adafruit_bme280.advanced import Adafruit_BME280_I2C
import pandas as pd
from datetime import datetime


# Inicializamos BMP:
i2c = busio.I2C(board.SCL, board.SDA) # Inicializa el bus I2C
bme280 = Adafruit_BME280_I2C(i2c, address=0x76)# Crea el objeto del sensor en la dirección 0x76
bme280.sea_level_pressure = 1013.25# Establece la presión a nivel del mar (opcional, para altitud)


# Funciones para GPS:
def run_example():

    print("SparkFun GPS Breakout - XA1110!")
    qwiicGPS = qwiic_titan_gps.QwiicTitanGps()

    if qwiicGPS.connected is False:
        print("Could not connect to to the SparkFun GPS Unit. Double check that\
              it's wired correctly.", file=sys.stderr)
        return

    qwiicGPS.begin()

    # Preparar carpeta y archivo CSV incremental
    base_dir = os.path.dirname(os.path.abspath(__file__))
    gps_dir = os.path.join(base_dir, 'gps')
    os.makedirs(gps_dir, exist_ok=True)

    max_idx = 0
    for fn in os.listdir(gps_dir):
        m = re.match(r"ubicacion_(\d+)\.csv$", fn)
        if m:
            try:
                idx = int(m.group(1))
                if idx > max_idx:
                    max_idx = idx
            except ValueError:
                pass

    next_idx = max_idx + 1
    csv_path = os.path.join(gps_dir, f"ubicacion_{next_idx}.csv")

    csvfile = open(csv_path, 'w', newline='')
    writer = csv.writer(csvfile)
    writer.writerow(['Time_RTC', 'Time_GPS', 'Latitude', 'Longitude', 'Altitude'])
    csvfile.flush()

    try:
        while True:
            try:
                ok = qwiicGPS.get_nmea_data()
            except Exception as e:
                # Ignorar errores de parsing (p. ej. sentencias GPGSV malformadas)
                print(f"[!] Error leyendo NMEA (ignorando): {e}")
                sleep(0.5)
                continue

            if ok is True:
                time_rtc = datetime.now().strftime("%H:%M:%S.%f")[:-3] # Hora de la raspberry
                # usar .get para evitar KeyError si faltan campos
                lat = -qwiicGPS.gnss_messages.get('Latitude', 'N/A') # GPS
                lon = -qwiicGPS.gnss_messages.get('Longitude', 'N/A') # GPS
                time_gps = qwiicGPS.gnss_messages.get('Time', 'N/A') # Hora GPS
                altitud = bme280.altitude # Leer altitud del sensor BMP280
                # Formatear tiempo si viene como lista [hh,mm,ss]
                if isinstance(time_gps, (list, tuple)):
                    try:
                        time_str = ':'.join(str(int(x)).zfill(2) for x in time_gps)
                    except Exception:
                        time_str = str(time_gps)
                else:
                    time_str = str(time_gps)

                print("Time_GPS{}, Time_RTC: {}, Latitude: {}, Longitude: {}, Altitude: {}".format(time_str, time_rtc, lat, lon, altitud))
                writer.writerow([time_rtc, time_str, lat, lon, altitud])
                csvfile.flush()

                mensaje = "Da:{}, La: {}, Lo: {}".format(time_rtc, float(lat), float(lon), float(altitud))

                subprocess.Popen(["python3", "envia_entrada.py", mensaje], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


            sleep(1)
    finally:
        try:
            csvfile.close()
        except Exception:
            pass


if __name__ == '__main__':
    try:
        run_example()
    except (KeyboardInterrupt, SystemExit) as exErr:
        print("Ending Basic Example.")
        sys.exit(0)
