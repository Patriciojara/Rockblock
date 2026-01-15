import sys
import pigpio
import time
from subprocess import Popen
#--------------------------- Lora-----------------------------------------------
import serial
import time
import RPi.GPIO as GPIO

SERIAL_PORT = "/dev/ttyUSB0"
BAUDRATE = 115200
RESET_PIN = 4

#subprocess.run("sudo pigpiod", shell=True)

# Parametro valvula

# Fin Parametro valvula




GPIO.setmode(GPIO.BCM)
GPIO.setup(RESET_PIN, GPIO.OUT, initial=GPIO.HIGH)

def reset_lora():
    GPIO.output(RESET_PIN, GPIO.LOW)
    time.sleep(0.2)
    GPIO.output(RESET_PIN, GPIO.HIGH)
    time.sleep(1)

def enviar_cmd(ser, cmd, delay=0.3):
    try:
        ser.write((cmd + "\r\n").encode())
        time.sleep(delay)
        respuesta = []
        while ser.in_waiting:
            line = ser.readline().decode(errors="ignore").strip()
            if line:
                print("📩", line)
                respuesta.append(line)
        return respuesta
    except Exception as e:
        print(f"[!] Error en '{cmd}': {e}")
        return []

def configurar_lora(ser):
    enviar_cmd(ser, "AT")
    enviar_cmd(ser, "AT+MODE=TEST")
    #enviar_cmd(ser, "AT+TEST=RFCFG,866,SF12,125,12,15,14,ON,OFF,OFF")

print("📡 Receptor LoRa-E5 iniciado...")
reset_lora()

def open(ser):
    # Activamos Pin PWM desde archivo python
    p = Popen([sys.executable, "pwm_gpio19.py"])
    # Configuramos Pin
    
    enviar_cmd(ser, f'AT+TEST=TXLRSTR,"{"Activando valvula..."}"', delay=2)
    #time.sleep(tiempo_seg-2)
    print("PWM detenido.")

    # Activamos Pin PWM
    

    # Mandamos Mensaje de activacion por Lora
    time.sleep(2)
    #print(f"PWM activado en el pin {PIN_PWM} con {frecuencia} Hz y {duty_percent:.1f}% duty cycle.")
    #time.sleep(tiempo_seg-2)
    # Enviar ACK
    ack_msg = f"ACK: {'Valvula abierta 4s'}"
    enviar_cmd(ser, f'AT+TEST=TXLRSTR,"{ack_msg}"', delay=2)
    print("✅ ACK enviado:", ack_msg)
    #pi.stop()
    print("PWM detenido.")
    


def close(ser):
    # Configuramos Pin
    p = Popen([sys.executable, "pwm_gpio12.py"])
    # Mandamos Mensaje de activacion por Lora
    time.sleep(2)
    enviar_cmd(ser, f'AT+TEST=TXLRSTR,"{"Cerrando valvula..."}"', delay=2)
    #print(f"PWM activado en el pin {PIN_PWM} con {frecuencia} Hz y {duty_percent:.1f}% duty cycle.")
    
    #pi.stop()
    print("PWM detenido.")
    
    # Enviar ACK
    ack_msg = f"ACK: {'Valvula Cerrada 12s'}"
    enviar_cmd(ser, f'AT+TEST=TXLRSTR,"{ack_msg}"', delay=2)
    print("✅ ACK enviado:", ack_msg)


def up(ser):
    # Configuramos Pin
    p = Popen([sys.executable, "pwm_gpio13.py"])
    # Mandamos Mensaje de activacion por Lora
    time.sleep(2)
    enviar_cmd(ser, f'AT+TEST=TXLRSTR,"{"Inyector Activo..."}"', delay=2)
    
    #pi.stop()
    print("PWM detenido.")
    
    # Enviar ACK
    ack_msg = f"ACK: {'Inyector Desactivado'}"
    enviar_cmd(ser, f'AT+TEST=TXLRSTR,"{ack_msg}"', delay=2)
    print("✅ ACK enviado:", ack_msg)

def rec():
    time.sleep(2)
    ack_msg = f"ACK: {'Grabando'}"
    enviar_cmd(ser, f'AT+TEST=TXLRSTR,"{ack_msg}"', delay=2)
    cmd = [
    "libcamera-vid",
    "-t", "0",
    "--width", "1280",
    "--height", "720",
    "-o", "video.h264"
    ]

    # Iniciar el proceso
    process = subprocess.Popen(cmd)



    print("Grabando...")
def rec_off():
    # Detener la grabación
    process.terminate()
    process.wait()
    print("Grabación finalizada.")
while True:
    try:
        # Solo configurar una vez
        with serial.Serial(SERIAL_PORT, BAUDRATE, timeout=2) as ser:
            configurar_lora(ser)
            enviar_cmd(ser, "AT+TEST=RXLRPKT", delay=1)
            while True:
                respuesta = enviar_cmd(ser, "", delay=2)  # NO enviar RXLRPKT de nuevo
                for line in respuesta:
                    if '+TEST: RX "' in line:
                        try:
                            hex_data = line.split('"')[1]
                            mensaje = bytes.fromhex(hex_data).decode()
                            print("📝 Recibido:", mensaje)

                            if mensaje == "open":
                                # Activar PWM
                                print("Activando valvula...")
                                open(ser)
                                # Volver a modo recepción
                                time.sleep(1)
                                enviar_cmd(ser, "AT+TEST=RXLRPKT", delay=1)
                            elif mensaje == "close":
                                # Activar PWM
                                print("Cerrando valvula...")
                                close(ser)
                                # Volver a modo recepción
                                time.sleep(1)
                                enviar_cmd(ser, "AT+TEST=RXLRPKT", delay=1)
                        
                            elif mensaje == "up":
                                # Activar PWM
                                print("Liberando liquido...")
                                up(ser)
                                # Volver a modo recepción
                                time.sleep(1)
                                enviar_cmd(ser, "AT+TEST=RXLRPKT", delay=1)                        
                            elif mensaje == "rec":
                                rec()

                            else:
                                time.sleep(1)
                                enviar_cmd(ser, "AT+TEST=RXLRPKT", delay=1)


                        except Exception as e:
                            print(f"⚠️ Error al decodificar el mensaje: {e}")
                time.sleep(1.5)


    except Exception as e:
        print(f"[!] Error de conexión serial: {e}")
        reset_lora()
        time.sleep(2)
    except KeyboardInterrupt:
        print("Interrumpido con Ctrl+C")

    finally:
        GPIO.cleanup()
        print("GPIO liberado y pigpio detenido")

#--------------------------- Lora-----------------------------------------------


