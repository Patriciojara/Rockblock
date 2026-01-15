
from time import sleep
import sys
import qwiic_titan_gps

def run_example():

    print("SparkFun GPS Breakout - XA1110!")
    qwiicGPS = qwiic_titan_gps.QwiicTitanGps()

    if qwiicGPS.connected is False:
        print("Could not connect to to the SparkFun GPS Unit. Double check that\
              it's wired correctly.", file=sys.stderr)
        return

    qwiicGPS.begin()

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
            print("Latitude: {}, Longitude: {}, Time: {}".format(lat, lon, t))

        sleep(1)


if __name__ == '__main__':
    try:
        run_example()
    except (KeyboardInterrupt, SystemExit) as exErr:
        print("Ending Basic Example.")
        sys.exit(0)
