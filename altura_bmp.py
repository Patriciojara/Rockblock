# Autor: Patricio Jara Quiroz
# Fecha: 18-10-2025
# Descripción: lee bmp y abre valvula segun velocidad de altura


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

# Leemos la altitud y calculamos la velocidad de ascenso
ventana = 100
altura = []
for _ in range(ventana):
    altura.append(bme280.altitude)

    time.sleep(0.1)
print("Ventana ok")
print(np.mean(altura))


