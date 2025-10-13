import serial, time

PORT = '/dev/serial0'
BAUD = 19200

def send(cmd, ser, wait=0.5):
    if not cmd.endswith('\r'):
        cmd += '\r'
    ser.reset_input_buffer()
    ser.write(cmd.encode('ascii'))
    time.sleep(wait)
    out = ser.read_all().decode(errors='ignore').strip()
    print(f">>> {cmd.strip()}\n{out}\n")
    return out

with serial.Serial(PORT, BAUD, timeout=1) as ser:
    print("\n--- Escucha de mensajes Iridium ---\n")
    send('ATE0', ser)
    send('AT', ser)
    send('AT+CSQ', ser)

    # Inicia sesión para recibir mensaje
    resp = send('AT+SBDIX', ser, wait=12)

    if '+SBDIX:' in resp:
        campos = resp.split(':')[1].split(',')
        if int(campos[2].strip()) == 1:  # Hay mensaje MT recibido
            print("📩 Nuevo mensaje recibido!")
            msg = send('AT+SBDRT', ser)
            print("Contenido del mensaje:\n", msg)
        else:
            print("No hay mensajes pendientes en la red Iridium.")
    else:
        print("Error: no se detectó respuesta válida.")
