import pigpio
import time
import subprocess
#--------------------------- Lora-----------------------------------------------

import time


subprocess.run("sudo pigpiod", shell=True)

# Parametro valvula
# Iniciar conexión con el daemon pigpio
pi = pigpio.pi()
if not pi.connected:
    print("Error: no se pudo conectar con el daemon pigpiod. ¿Está corriendo?")
    exit(1)

# Configuramos Pin
PIN_PWM = 19  # Puedes cambiar este pin
frecuencia = 25
duty_percent=25
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


