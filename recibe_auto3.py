import serial, time
import sys
from datetime import datetime

# === CONFIGURACIÓN SERIAL ===
PORT = '/dev/serial0'   # cambia si usas otro puerto
BAUD = 19200

# === FUNCIONES AUXILIARES ===
def send(cmd, ser, wait=1):
    """Envía comando AT y devuelve respuesta limpia"""
    #if not cmd.endswith('\r'):
    #    cmd += '\r'
    ser.reset_input_buffer()
    ser.write(cmd.encode('ascii'))
    time.sleep(wait)
    out = ser.read_all().decode(errors='ignore').strip()
    print(f">>> {cmd.strip()}\n{out}\n")
    return out

def get_signal(ser):
    """Obtiene nivel de señal (0–5)"""
    resp = send('AT+CSQ', ser)
    if '+CSQ:' in resp:
        try:
            return int(resp.split(':')[1].split()[0])
        except:
            return 0
    return 0

# === PROGRAMA PRINCIPAL ===
with serial.Serial(PORT, BAUD, timeout=1) as ser:
    print("\n--- RockBLOCK Prueba de Recibo ---\n")
    send('ATE0', ser)   # desactivar eco
    send('AT', ser)
    # Esperar buena señal (>=2)
    print("\U0001f4e1 Buscando señal Iridium...")
    
    csq = 0

    for _ in range(20):   # intenta 20 veces (≈20 s)
        csq = get_signal(ser)
        print(f"Nivel de señal: {csq}")
        if csq >= 2:
            break
        time.sleep(1)

    if csq < 2:
        print("\u2716 Señal insuficiente, no se intentará recibir.")
    else:
        # Construir mensaje con hora local
        #hora = datetime.now().strftime("%H:%M:%S")
        #mensaje_entrada = sys.argv[1]
        #print(f'\u2709 {hora} Mensaje entrada {mensaje_entrada}')
        send(f'AT&K0\r', ser, wait=2) # desactivar flow control
        # Cargar mensaje para lectura
        resp = send('AT+SBDIX\r', ser, wait=30)  # Pregunta si hay mensajes

        # Analizar resultado
        if '+SBDIX:' in resp:
            cod = resp.split(':')[1].split(',')[0].strip()
            if cod == '0':
                print("\u2714 Mensaje enviado correctamente al satélite.")
            else:
                print(f"\u26A0 Error de envío (código {cod}). Revisa señal o plan.")
        else:
            print("\u26A0 No se detectó respuesta válida de SBDIX.")
