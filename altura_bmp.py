# Autor: Patricio Jara Quiroz
# Fecha: 18-10-2025
# Descripción: lee bmp y abre valvula segun velocidad de altura


import adafruit_ds3231
import numpy as np
import time
import board
import busio
from adafruit_bme280.advanced import Adafruit_BME280_I2C

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
ventana = 2
altura = []
for _ in range(ventana):
    t = rtc.datetime
    time_rtc = f"{t.tm_hour}:{t.tm_min:02}:{t.tm_sec:02}"
    altura.append((time_rtc, bme280.altitude))
    print(f"Hora RTC: {time_rtc} - Altitud: {bme280.altitude:.2f} m")
    time.sleep(1)
print("Ventana ok")
hora, altitud = altura[0:10]
print(np.mean(altitud))


