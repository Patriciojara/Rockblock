import serial
import time

# Abrir puerto serial (cambia '/dev/serial0' si es necesario)
ser = serial.Serial('/dev/serial0', 19200, timeout=1)

# Comando AT para verificar conexión
ser.write(b'AT+SBDIX?\r\n')  # Envía el comando AT para probar la comunicación
time.sleep(1)  # Espera para que el módulo responda

# Leer la respuesta
response = ser.read(100)  # Lee hasta 100 bytes
print("Respuesta:", response.decode())

# Cerrar la conexión
ser.close()
