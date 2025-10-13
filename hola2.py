import serial, time

PORT = '/dev/serial0'
BAUD = 19200

def send(cmd, ser, wait=0.3):
    if not cmd.endswith('\r'):
        cmd += '\r'
    ser.reset_input_buffer()
    ser.write(cmd.encode('ascii'))
    time.sleep(wait)
    out = ser.read_all().decode(errors='ignore')
    print(f">>> {cmd.strip()}\n{out.strip()}\n")
    return out

with serial.Serial(PORT, BAUD, timeout=0.2) as ser:
    # Opcional: desactiva eco para que no “duplicque” los comandos
    send('ATE0', ser)

    # Prueba básica
    send('AT', ser)
    send('AT+CSQ', ser)          # 0..5 (>=2 ya es usable)

    # --- Forma 1: inline (tu forma) ---
    msg = 'Saludos_profe_desde__-33.49404245932506, -70.62432000455497,Temp=17C'
    send(f'AT+SBDWT={msg}', ser) # Espera "OK" (buffer MO cargado)

    # Si ya tienes plan activo y buena señal, descomenta para enviar:
    # send('AT+SBDIX', ser)      # Busca satélite, envía/recibe
    # send('AT+SBDSX', ser)      # Estado extendido del último intento

    # --- Forma 2: interactiva (por si la prefieres) ---
    # out = send('AT+SBDWT', ser)   # Espera "READY"
    # if 'READY' in out:
    #     ser.write(b'Saludo_interactivo\r')  # tu texto (no hace falta \r)
    #     ser.write(bytes([26]))              # Ctrl+Z (0x1A) para terminar
    #     time.sleep(0.5)
    #     print(ser.read_all().decode(errors='ignore'))
