# Autor: Patricio Jara Quiroz
# Fecha: 08-10-2025
# Descripción: Activa subida de Radiosonda.

import pigpio
import time
import subprocess
#--------------------------- Lora-----------------------------------------------
import serial
import time
import RPi.GPIO as GPIO

SERIAL_PORT = "/dev/serial0"
BAUDRATE = 115200
RESET_PIN = 4

subprocess.run("sudo pigpiod", shell=True)

# Parametro valvula
# Iniciar conexión con el daemon pigpio
pi = pigpio.pi()
if not pi.connected:
    print("Error: no se pudo conectar con el daemon pigpiod. ¿Está corriendo?")
    exit(1)
PIN_PWM = 18  # Puedes cambiar este pin
frecuencia = 1
duty_percent=100
tiempo_seg=4
duty = int((duty_percent / 100) * 255)
# Fin Parametro valvula


GPIO.setmode(GPIO.BCM)
GPIO.setup(RESET_PIN, GPIO.OUT, initial=GPIO.HIGH)




# Configuramos Pin
PIN_PWM = 18  # Puedes cambiar este pin
frecuencia = 25
duty_percent=50
tiempo_seg=12
duty = int((duty_percent / 100) * 255)

# Activamos Pin PWM
pi.set_mode(PIN_PWM, pigpio.OUTPUT)
pi.set_PWM_frequency(PIN_PWM, frecuencia)
pi.set_PWM_dutycycle(PIN_PWM, duty)


print(f"PWM activado en el pin {PIN_PWM} con {frecuencia} Hz y {duty_percent:.1f}% duty cycle.")
time.sleep(tiempo_seg)
pi.set_PWM_dutycycle(PIN_PWM, 0)
pi.stop()
print("PWM detenido.")


#--------------------------- Lora-----------------------------------------------


