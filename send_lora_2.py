#!/usr/bin/env python3
"""
send_lora.py — emisor simple para módulo LoRa (AT+TEST)

Uso:
  - Directo: python send_lora.py open
  - Interactivo (si ejecutas solo python send_lora.py): puerto preseleccionado COM7 en Windows

Requiere: pyserial (`pip install pyserial`)
"""
import sys
import time
import argparse
import serial

# Definimos el puerto COM que se conecta el lora al PC.
DEFAULT_PORT = "COM7"#'/dev/ttyUSB0' if sys.platform != 'win32' else 'COM7'
DEFAULT_BAUD = 115200 # Velocidad de comunicación serial funciona con 115200

ALLOWED = {'up', 'open', 'rec', 'close'} # Comandos permitidos

def enviar_cmd(ser, cmd=None, delay=0.2, read_timeout=1.0):
    """Enviar una línea (si cmd) y leer respuesta disponible."""
    if cmd:
        ser.write((cmd + "\r\n").encode())
    time.sleep(delay)
    ser.timeout = read_timeout
    out = []

    try:
        while True:
            line = ser.readline()
            if not line:
                break
            try: 
                text = line.decode(errors='ignore').strip()
            except Exception:
                text = repr(line)
            if text:
                print("<-", text)
                out.append(text)
    except Exception as e:
        print("[!] Error leyendo serial:", e)
    return out

def _parse_lora_rx(line):
    """Parsea líneas del formato +TEST: RX "HEX..." y devuelve el texto decodificado si es posible."""
    if '+TEST: RX "' in line:
        try:
            hex_data = line.split('"')[1]
            payload = bytes.fromhex(hex_data)
            try:
                text = payload.decode(errors='ignore')
                return text
            except Exception:
                return repr(payload)
        except Exception:
            return None
    return None

def main():
    p = argparse.ArgumentParser(description='Enviar comandos por LoRa (módulo AT)')
    p.add_argument('command', nargs='?', choices=sorted(ALLOWED), help='Comando a enviar (opcional)')
    p.add_argument('--port', '-p', default=DEFAULT_PORT, help='Puerto serial (ej: /dev/ttyUSB0 o COM3) o número de puerto (7)')
    p.add_argument('--baud', '-b', type=int, default=DEFAULT_BAUD)
    p.add_argument('--wait-ack', action='store_true', help='Esperar ACK/respuesta del receptor')
    p.add_argument('--timeout', '-t', type=float, default=5.0, help='Tiempo máximo (s) para esperar ACK')
    args = p.parse_args()

    cmd = args.command

    # modo interactivo si no se pasó comando
    port_arg = args.port
    #if cmd is None:
    print("Modo interactivo — puerto preseleccionado:", DEFAULT_PORT)
    
    # Comandos para enviar a través de LoRa
    cmds = "/".join(sorted(ALLOWED)) # "close/open/rec/up" comandos permitidos
    cmd_input = input(f"Comando ({cmds}) [open]: ").strip().lower()
    cmd = cmd_input or 'open'
    if cmd not in ALLOWED:
        print("Comando no válido.")
        sys.exit(2)

    port_arg = DEFAULT_PORT
    try:
        with serial.Serial(port_arg, args.baud, timeout=1) as ser:
            print(f"Conectado a {port_arg} @ {args.baud}")
            enviar_cmd(ser, "AT", delay=0.2) # Comando AT básico para verificar conexión
            enviar_cmd(ser, "AT+MODE=TEST", delay=0.2)  # Modo de prueba LoRa para comunicacion directa.

            send = f'AT+TEST=TXLRSTR,"{cmd}"' # Comando para enviar datos LoRa
            print(">", send) # Mostrar comando enviado
            enviar_cmd(ser, send, delay=0.3) # Enviar comando LoRa
            print("Comando enviado.")

            # Ahora se esperara un recepcion de un ACK (mensaje desde otro lora)
      
            print(f"Esperando ACK ({args.timeout}s)...")
            enviar_cmd(ser, "AT+TEST=RXLRPKT", delay=0.2) # Comando para recibir paquetes LoRa
            t0 = time.time()
            while time.time() - t0 < args.timeout:
                lines = enviar_cmd(ser, None, delay=0.5, read_timeout=0.5) # Leer líneas disponibles
                for l in lines:
                    # intentar parsear payload LoRa
                    decoded = _parse_lora_rx(l)
                    if decoded is not None:
                        print("ACK recibido (decoded):", decoded) 
                        return
                    if 'ACK' in l:
                        print("ACK recibido:", l)
                        return
            print("Tiempo de espera agotado.")

    except serial.SerialException as e:
        print(f"Error abriendo puerto serial {port_arg}: {e}")
        sys.exit(2)

if __name__ == '__main__':
    main()
