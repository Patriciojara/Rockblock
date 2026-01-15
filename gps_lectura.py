
from time import sleep
import sys
import os
import csv
import re
import qwiic_titan_gps

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
    writer.writerow(['Time', 'Latitude', 'Longitude'])
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
                # usar .get para evitar KeyError si faltan campos
                lat = qwiicGPS.gnss_messages.get('Latitude', 'N/A')
                lon = qwiicGPS.gnss_messages.get('Longitude', 'N/A')
                t = qwiicGPS.gnss_messages.get('Time', 'N/A')

                # Formatear tiempo si viene como lista [hh,mm,ss]
                if isinstance(t, (list, tuple)):
                    try:
                        time_str = ':'.join(str(int(x)).zfill(2) for x in t)
                    except Exception:
                        time_str = str(t)
                else:
                    time_str = str(t)

                print("Latitude: {}, Longitude: {}, Time: {}".format(lat, lon, time_str))
                writer.writerow([time_str, lat, lon])
                csvfile.flush()

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
