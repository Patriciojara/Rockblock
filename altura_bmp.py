# Autor: Patricio Jara Quiroz
# Fecha: 18-10-2025
# Descripción: lee bmp y abre valvula segun velocidad de altura

print(
"Importando librerias...")

import subprocess
import adafruit_ds3231
import numpy as np
import time
import board
import busio
from adafruit_bme280.advanced import Adafruit_BME280_I2C
import pandas as pd
from datetime import datetime


print(
"Configurando sensores")
# Inicializa el bus I2C
i2c = busio.I2C(board.SCL, board.SDA)

# Crea el objeto del sensor en la dirección 0x76
bme280 = Adafruit_BME280_I2C(i2c, address=0x76)

# Establece la presión a nivel del mar (opcional, para altitud)
bme280.sea_level_pressure = 1013.25




# ------------RTC------------------

i2c_ds3231 = board.I2C()  # uses board.SCL and board.SDA ds3231
# i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
rtc = adafruit_ds3231.DS3231(i2c_ds3231)

# Lookup table for names of days (nicer printing).
days = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")



# Leemos la altitud y calculamos la velocidad de ascenso
ventana = 10
altura = []
hora = []
print("Leyendo altitud...")
while True:
    altura = []
    hora = []
    for _ in range(ventana):
        #t = rtc.datetime
        #now = datetime.now()  # del sistema
        
        # time_rtc = f"{t.tm_hour}:{t.tm_min:02}:{t.tm_sec:02}" Hora del rtc
        # time_rtc_ms = f"{t.tm_hour:02}:{t.tm_min:02}:{t.tm_sec:02}.{int(now.microsecond/1000):03d}" Falla ya que retrocede los milisegundos
        
        time_system = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        hora.append(time_system)
        altura.append(bme280.altitude)
        print(f"Hora RTC: {time_system} - Altitud: {bme280.altitude:.2f} m")
        time.sleep(0.01)
    print("Ventana ok")
    print(np.mean(altura))

    print("Calculando velocidad de ascenso...")
    t = pd.to_datetime(hora)
    t_seg = (t - t[0]).total_seconds().to_numpy()
    m, b = np.polyfit(t_seg, altura, deg=1)
    print(f"Velocidad de ascenso: {m:.2f} m/s")
    if m >= 0.5:
        print("🎈Abriendo valvula...🎈")
        subprocess.Popen(["python3", "buzzer.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    else: 
        print("✅Velocidad de ascenso dentro de limites.")