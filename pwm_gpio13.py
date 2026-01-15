#!/usr/bin/env python3

"""

pwm_gpio12.py

Activa PWM en GPIO12 (pin físico 32) a 25Hz y 50% duty durante 5 segundos.

Ejecutar en Raspberry Pi con:
    sudo python3 pwm_gpio12.py aun que funciona sin sudo.

"""
import time
import sys
import signal
# Intentar importar RPi.GPIO y manejar el error si no está disponible o si se corre desde un pc.
try:
    import RPi.GPIO as GPIO
except Exception as e:
    sys.exit("Este script debe ejecutarse en una Raspberry Pi con RPi.GPIO instalado: " + str(e))

PIN = 13  # BCM numbering (GPIO13), pin físico 33
FREQ = 25  # Hz
DUTY = 50  # %
DURATION = 5  # segundos

# objeto PWM global para que el handler de señales pueda detenerlo
pwm = None

def _cleanup():
    global pwm
    try:
        if pwm is not None:
            pwm.stop()
    except Exception:
        pass
    try:
        GPIO.cleanup()
    except Exception:
        pass

def _signal_handler(signum, frame):
    _cleanup()
    sys.exit(0)

def main():
    global pwm
    # registrar manejadores para SIGTERM y SIGINT (Ctrl+C)
    signal.signal(signal.SIGTERM, _signal_handler)
    signal.signal(signal.SIGINT, _signal_handler)

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PIN, GPIO.OUT)

    pwm = GPIO.PWM(PIN, FREQ)
    try:
        pwm.start(DUTY)
        time.sleep(DURATION)
    except KeyboardInterrupt:
        pass
    finally:
        _cleanup()

if __name__ == '__main__':
    main()
