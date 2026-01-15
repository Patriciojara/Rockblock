#!/usr/bin/env python3
"""
pwm_gpio12.py

Activa PWM en GPIO12 (pin físico 32) a 25Hz y 50% duty durante 5 segundos.

Ejecutar en Raspberry Pi con:
    sudo python3 pwm_gpio12.py

"""
import time
import sys
try:
    import RPi.GPIO as GPIO
except Exception as e:
    sys.exit("Este script debe ejecutarse en una Raspberry Pi con RPi.GPIO instalado: " + str(e))

PIN = 12  # BCM numbering (GPIO12), pin físico 32
FREQ = 25  # Hz
DUTY = 50  # %
DURATION = 5  # segundos

def main():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PIN, GPIO.OUT)

    pwm = GPIO.PWM(PIN, FREQ)
    try:
        pwm.start(DUTY)
        time.sleep(DURATION)
    except KeyboardInterrupt:
        pass
    finally:
        pwm.stop()
        GPIO.cleanup()

if __name__ == '__main__':
    main()
