import serial, time, re

PORT = '/dev/serial0'
BAUD = 19200

def open_port():
    ser = serial.Serial(
        PORT,
        BAUD,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=0.5,        # lectura no bloqueante
        xonxoff=False,      # SIN software flow control
        rtscts=False,       # SIN hardware flow control
        dsrdtr=False
    )
    time.sleep(1.5)        # deje arrancar al módem
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    return ser

def send(ser, cmd, max_wait_s=3.0, show=True):
    """Envía 'cmd\\r' y lee hasta ver 'OK'/'ERROR' o agotar tiempo."""
    if not cmd.endswith('\r'):
        cmd += '\r'
    ser.write(cmd.encode('ascii'))
    deadline = time.time() + max_wait_s
    buf = b''
    while time.time() < deadline:
        chunk = ser.read(512)
        if chunk:
            buf += chunk
            text = buf.decode(errors='ignore')
            # Normalizamos saltos
            if 'OK' in text or 'ERROR' in text:
                break
        else:
            time.sleep(0.05)
    out = buf.decode(errors='ignore')
    if show:
        print(f">>> {cmd.strip()}\n{out.strip()}\n")
    return out

def get_csq(text):
    m = re.search(r'\+CSQ:\s*(\d+)', text)
    return int(m.group(1)) if m else None

def parse_sbdix(text):
    # Acepta espacios y variaciones
    m = re.search(r'\+SBDIX:\s*(-?\d+),\s*(\d+),\s*(-?\d+),\s*(\d+),\s*(\d+),\s*(-?\d+)', text)
    if not m:
        return None
    mo_code   = int(m.group(1))
    mo_momsn  = int(m.group(2))
    mt_code   = int(m.group(3))
    mt_momsn  = int(m.group(4))
    mt_len    = int(m.group(5))
    ext_err   = int(m.group(6))
    return (mo_code, mo_momsn, mt_code, mt_momsn, mt_len, ext_err)

with open_port() as ser:
    # Sin eco
    send(ser, 'ATE0', 2.0)

    # Golpecitos de "AT" para sincronizar
    synced = False
    for _ in range(5):
        out = send(ser, 'AT', 1.0)
        if 'OK' in out:
            synced = True
            break
        time.sleep(0.2)
    if not synced:
        print("⚠️ No hay respuesta a AT. Revisa cableado/baud/alimentación.")
        raise SystemExit

    # Ver señal (puede tardar unos segundos en aparecer)
    csq_val = None
    for _ in range(10):
        out = send(ser, 'AT+CSQ', 2.0, show=True)
        csq_val = get_csq(out)
        if csq_val is not None:
            break
        time.sleep(0.5)
    print(f"CSQ={csq_val if csq_val is not None else 'N/A'}")

    # Intento de sesión SBD (hasta 60 s de espera)
    # OJO: si no tienes plan activo o no hay señal suficiente, fallará con código 18/32/35.
    out = send(ser, 'AT+SBDIX', max_wait_s=60.0, show=True)
    parsed = parse_sbdix(out)

    if not parsed:
        print("⚠️ No se detectó respuesta válida de SBDIX (no apareció '+SBDIX:' ni 'OK').")
        print("   Sube max_wait_s a 90 s y verifica que no estás usando '\\r\\n'.")
    else:
        mo_code, mo_momsn, mt_code, mt_momsn, mt_len, ext_err = parsed
        print(f"SBDIX => MO:{mo_code},{mo_momsn}  MT:{mt_code},{mt_momsn} len={mt_len} ext={ext_err}")
        if mt_len > 0:
            # Leer el mensaje recibido
            mt = send(ser, 'AT+SBDRT', 3.0, show=True)
