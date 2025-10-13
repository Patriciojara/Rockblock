import serial, time
import sys
from datetime import datetime

# === CONFIGURACIÓN SERIAL ===
PORT = '/dev/serial0'   # cambia si usas otro puerto
BAUD = 19200

# === FUNCIONES AUXILIARES ===
def send(cmd, ser, wait=0.5):
    """Envía comando AT y devuelve respuesta limpia"""
    if not cmd.endswith('\r'):
        cmd += '\r'
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
    print("\n--- RockBLOCK Prueba de Envío con hora ---\n")
    send('ATE0', ser)   # desactivar eco
    send('AT', ser)

    # Esperar buena señal (>=2)
    print("Buscando señal Iridium...")
    csq = 0
    mensaje_entrada = sys.argv
    print(f'Mensaje entrada {mensaje_entrada}.')
    for _ in range(20):   # intenta 20 veces (≈20 s)
        csq = get_signal(ser)
        print(f"Nivel de señal: {csq}")
        if csq >= 2:
            break
        time.sleep(1)

    if csq < 2:
        print("❌ Señal insuficiente, no se intentará enviar.")
    else:
        # Construir mensaje con hora local
        hora = datetime.now().strftime("%H:%M:%S")
        contador = 1  # puedes incrementar en un bucle si quieres mandar varios
        mensaje = f"{hora}: Saludos desde SUCHAI-Flight-Sofware, lat:-21.00938,lon: -70.1234493."
        mensaje_entrada = sys.argv
        print(f'Mensaje entrada {mensaje_entrada}.')
        print(f"📤 Enviando: {mensaje}")
        # Cargar mensaje
        send(f'AT+SBDWT={mensaje_entrada}', ser)

        # Ejecutar sesión SBD
        resp = send('AT+SBDIX', ser, wait=12)  # espera más para el enlace

        # Analizar resultado
        if '+SBDIX:' in resp:
            cod = resp.split(':')[1].split(',')[0].strip()
            if cod == '0':
                print("✅ Mensaje enviado correctamente al satélite.")
            else:
                print(f"⚠️ Error de envío (código {cod}). Revisa señal o plan.")
        else:
            print("⚠️ No se detectó respuesta válida de SBDIX.")
