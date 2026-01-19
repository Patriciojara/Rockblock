
from time import sleep
import sys
import os
import csv
import re
import qwiic_titan_gps
import subprocess
import threading
import queue


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


current_proc = None
current_proc_lock = threading.Lock()

def rockblock_send(message):
    """Encola el mensaje para envío en background y retorna inmediatamente."""
    send_queue.put(message)


def rockblock_send_fast(message, timeout=20):
    """Vacía la cola de envío y envía `message` inmediatamente (sin encolar).

    - Borra cualquier mensaje pendiente en `send_queue`.
    - Llama directamente a `envia_entrada.py` y muestra stdout/stderr.
    Devuelve el objeto `subprocess.CompletedProcess` o `None` en caso de error/timeout.
    """
    # limpiar la cola para que solo el mensaje actual sea enviado
    try:
        while True:
            item = send_queue.get_nowait()
            send_queue.task_done()
    except queue.Empty:
        pass

    try:
        print(f"Fast send: {message}")
        proc = subprocess.run(["sudo", "python3", "envia_entrada.py", message], capture_output=True, text=True, timeout=timeout)
        if proc.stdout:
            print("envia_entrada stdout:\n", proc.stdout)
        if proc.stderr:
            print("envia_entrada stderr:\n", proc.stderr, file=sys.stderr)
        return proc
    except subprocess.TimeoutExpired as e:
        print(f"[!] Timeout en rockblock_send_fast: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"[!] Error en rockblock_send_fast: {e}", file=sys.stderr)
        return None


def rockblock_send_fast_sin_queue(message, timeout=None):
    """Lanza `envia_entrada.py` con Popen sólo si no hay un proceso activo.

    - Si ya hay un proceso en ejecución, no hace nada y devuelve False.
    - Si no hay proceso o ya terminó, inicia uno nuevo y lee su salida en
      un hilo en background (no bloquea el bucle principal).
    - Devuelve True si inició un proceso, False si se omitió, None en error.
    """
    global current_proc
    try:
        with current_proc_lock:
            if current_proc is not None:
                if current_proc.poll() is None:
                    # El proceso todavía corre: no iniciar otro
                    print("Envio en curso; omitiendo nuevo envío.")
                    return False
                else:
                    # El proceso terminó: limpiar
                    current_proc = None

            print(f"Fast Popen send: {message}")
            proc = subprocess.Popen(["sudo", "python3", "envia_entrada.py", message], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            current_proc = proc

        # Leer la salida en un hilo para no bloquear el loop principal
        def _reader(p: subprocess.Popen):
            global current_proc
            try:
                if timeout:
                    out, err = p.communicate(timeout=timeout)
                else:
                    out, err = p.communicate()
            except subprocess.TimeoutExpired:
                try:
                    p.kill()
                except Exception:
                    pass
                out, err = p.communicate()
                print("[!] Timeout leyendo proceso hijo", file=sys.stderr)

            if out:
                print("envia_entrada stdout:\n", out)
            if err:
                print("envia_entrada stderr:\n", err, file=sys.stderr)

            with current_proc_lock:
                if current_proc is p:
                    current_proc = None

        t = threading.Thread(target=_reader, args=(proc,), daemon=True)
        t.start()
        return True
    except Exception as e:
        print(f"[!] Error en rockblock_send_fast_sin_queue: {e}", file=sys.stderr)
        return None

# Cola y worker para enviar en background (no bloquea la adquisición de datos)
send_queue = queue.Queue()

def sender_worker(q):
    while True:
        msg = q.get()
        if msg is None:
            break
        try:
            print(f"Worker: enviando mensaje: {msg}")
            proc = subprocess.run(["sudo", "python3", "envia_entrada.py", msg], capture_output=True, text=True)
            if proc.stdout:
                print("envia_entrada stdout:\n", proc.stdout)
            if proc.stderr:
                print("envia_entrada stderr:\n", proc.stderr, file=sys.stderr)
        except Exception as e:
            print("Error en sender_worker:", e, file=sys.stderr)
        finally:
            q.task_done()

# arrancar worker (daemon para que no impida el cierre)
sender_thread = threading.Thread(target=sender_worker, args=(send_queue,), daemon=True)
sender_thread.start()

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
                time_rtc = datetime.now().strftime("%H:%M:%S") # Hora de la raspberry (sin milisegundos)
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

                print("Time_GPS: {}, Time_RTC: {}, Latitude: {}, Longitude: {}, Altitude: {}".format(time_str, time_rtc, lat, lon, altitud))
                writer.writerow([time_rtc, time_str, lat, lon, altitud])
                csvfile.flush()

                mensaje = "Da:{}, La: {:.7f}, Lo: {:.7f}, al: {:.3f}".format(time_rtc, float(lat), float(lon), float(altitud))
                rockblock_send_fast_sin_queue(mensaje)
                #subprocess.Popen(["python3", "envia_entrada.py", mensaje], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


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
