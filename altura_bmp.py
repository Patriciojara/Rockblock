# Autor: Patricio Jara Quiroz
# Fecha: 18-10-2025
# Descripción: lee bmp y abre valvula segun velocidad de altura

print(
"Importando librerias...")


import adafruit_ds3231
import numpy as np
import time
import board
import busio
from adafruit_bme280.advanced import Adafruit_BME280_I2C
from sklearn.linear_model import LinearRegression

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
ventana = 3
altura = []
hora = []
print("Leyendo altitud...")
for _ in range(ventana):
    t = rtc.datetime
    time_rtc = f"{t.tm_hour}:{t.tm_min:02}:{t.tm_sec:02}"
    hora.append(time_rtc)
    altura.append(bme280.altitude)
    print(f"Hora RTC: {time_rtc} - Altitud: {bme280.altitude:.2f} m")
    time.sleep(1)
print("Ventana ok")
print(np.mean(altura))

print("Calculando velocidad de ascenso...")



# Sample data
#x = np.array([1, 2, 3, 4, 5]).reshape(-1, 1)  # Reshape for scikit-learn
#y = np.array([2, 4, 5, 4, 5])

# Create model instance
model = LinearRegression()

# Fit the model
model.fit(hora, altura)

# Get model parameters
print(f"Slope (B1): {model.coef_[0]}")
print(f"Intercept (B0): {model.intercept_}")

# Predict values
y_pred = model.predict(x)
print("Predicted values:", y_pred)
