#!/usr/bin/env python3
"""
send_lora_clean.py — emisor simple para módulo LoRa (AT+TEST)

Uso:
  - Directo: python send_lora_clean.py open
  - Interactivo (si ejecutas solo python send_lora_clean.py): puerto preseleccionado COM7 en Windows

Requiere: pyserial (`pip install pyserial`)
"""
import sys
import time
import argparse
try:
    import serial
except Exception:
    sys.exit("Instala pyserial: pip install pyserial")

DEFAULT_PORT = 'COM7'
DEFAULT_BAUD = 115200


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


def main_listen(port=DEFAULT_PORT, baud=DEFAULT_BAUD):
    """Abrir puerto y entrar en modo escucha, imprimiendo mensajes decodificados."""
    try:
        with serial.Serial(port, baud, timeout=1) as ser:
            print(f"Conectado a {port} @ {baud}")
            # Inicializar módulo
            ser.write(b"AT\r\n")
            time.sleep(0.2)
            ser.write(b"AT+MODE=TEST\r\n")
            time.sleep(0.2)

            # Permitir enviar un mensaje antes de entrar en modo escucha
            try:
                pre = input("Mensaje a enviar antes de escuchar (ENTER para omitir): ").strip()
            except Exception:
                pre = ''
            if pre:
                send_cmd = f'AT+TEST=TXLRSTR,"{pre}"\r\n'
                ser.write(send_cmd.encode())
                time.sleep(0.3)
                # leer respuesta corta
                t0 = time.time()
                while time.time() - t0 < 1.0:
                    r = ser.readline()
                    if not r:
                        break
                    try:
                        print("<-", r.decode(errors='ignore').strip())
                    except Exception:
                        print("<-", repr(r))

            # pasar a recepción
            ser.write(b"AT+TEST=RXLRPKT\r\n")
            print("Entrando en modo escucha (presiona Ctrl+C para salir)...")
            while True:
                line = ser.readline()
                if not line:
                    continue
                try:
                    text = line.decode(errors='ignore').strip()
                except Exception:
                    text = repr(line)
                if text:
                    decoded = _parse_lora_rx(text)
                    if decoded is not None:
                        print("<- RX (decoded):", decoded)
                    else:
                        print("<-", text)
    except serial.SerialException as e:
        print(f"Error abriendo puerto serial {port}: {e}")
        sys.exit(2)
    except KeyboardInterrupt:
        print("\nInterrumpido por usuario. Saliendo.")


if __name__ == '__main__':
    main_listen()
