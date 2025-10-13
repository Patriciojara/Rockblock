import serial, time, re, csv
from datetime import datetime, timezone

PORT = '/dev/serial0'   # Cambia si usas otro puerto
BAUD = 19200
POLL_SECONDS = 60       # Cada cuánto consultar al satélite
SBDIX_WAIT = 120.0       # Espera máxima para SBDIX (s). Puedes subir a 90.

TXT_LOG = 'mensajes_recibidos.txt'
CSV_LOG = 'mensajes_recibidos.csv'

def open_port():
    ser = serial.Serial(
        PORT, BAUD,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=0.5,
        xonxoff=False,
        rtscts=False,
        dsrdtr=False
    )
    time.sleep(1.5)
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    return ser

def send(ser, cmd, max_wait_s=3.0, verbose=True):
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
            txt = buf.decode(errors='ignore')
            if 'OK' in txt or 'ERROR' in txt:
                break
        else:
            time.sleep(0.05)
    out = buf.decode(errors='ignore').strip()
    if verbose:
        print(f">>> {cmd.strip()}\n{out.strip()}\n")
    return out

def parse_sbdix(text):
    m = re.search(r'\+SBDIX:\s*(-?\d+),\s*(\d+),\s*(-?\d+),\s*(\d+),\s*(\d+),\s*(-?\d+)', text)
    if not m:
        return None
    return tuple(int(g) for g in m.groups())  # (mo, mo_id, mt, mt_id, mt_len, ext)

def extract_sbdrt_payload(text):
    # Devuelve el bloque después de "+SBDRT:" hasta "OK"
    if '+SBDRT' not in text:
        return ''
    # Quita encabezado y 'OK'
    lines = text.splitlines()
    out_lines = []
    take = False
    for ln in lines:
        if ln.strip().startswith('+SBDRT'):
            take = True
            continue
        if take:
            if ln.strip() == 'OK':
                break
            out_lines.append(ln)
    # Une preservando posibles comas, etc.
    payload = '\n'.join(out_lines).strip()
    return payload

def ensure_csv_header():
    try:
        with open(CSV_LOG, 'x', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(['ts_local', 'ts_utc', 'mo_status', 'mo_momsn', 'mt_status', 'mt_momsn', 'mt_len', 'ext_status', 'payload'])
    except FileExistsError:
        pass

def append_logs(payload, sbdix_tuple):
    ts_local = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ts_utc   = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    mo, mo_id, mt, mt_id, mt_len, ext = sbdix_tuple

    # TXT
    with open(TXT_LOG, 'a', encoding='utf-8') as f:
        f.write(f"[{ts_local} | UTC {ts_utc}]  SBDIX: MO={mo},{mo_id}  MT={mt},{mt_id} len={mt_len} ext={ext}\n")
        f.write(payload + "\n")
        f.write("-"*60 + "\n")

    # CSV
    ensure_csv_header()
    with open(CSV_LOG, 'a', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow([ts_local, ts_utc, mo, mo_id, mt, mt_id, mt_len, ext, payload])


def get_signal(ser):
    """Obtiene nivel de señal (0–5)"""
    resp = send('AT+CSQ', ser)
    if '+CSQ:' in resp:
        try:
            return int(resp.split(':')[1].split()[0])
        except:
            return 0
    return 0


csq=0
def main():
    with open_port() as ser:
        print("\n--- Receptor RockBLOCK: guardado automático de mensajes MT ---\n")
        send(ser, 'ATE0', 2.0)  # sin eco
        # Sincroniza con el módem
        for _ in range(5):
            if 'OK' in send(ser, 'AT', 1.0):
                break
            time.sleep(0.2)

        # Bucle de escucha
        while True:
            # (Opcional) ver señal actual
            #csq = get_signal(ser)
            signal = send(ser, 'AT+CSQ', 2.0)
            if "+CSQ:" in signal:
                try:
                    csq= int(signal.split(":")[1].split()[0])
                except:
                    csq =  0
            #return 0
            else:
                csq = inte
            if signal >=2:
                
            
                
            
            # Sesión para recibir
                out = send(ser, 'AT+SBDIX', max_wait_s=SBDIX_WAIT)
                sbd = parse_sbdix(out)
                if not sbd:
                    print("⚠️ No se detectó respuesta válida de SBDIX. Reintentando en unos segundos...")
                    time.sleep(POLL_SECONDS)
                    continue

                mo, mo_id, mt, mt_id, mt_len, ext = sbd
                if mt_len > 0:
                    print(f"📩 MT recibido (len={mt_len} bytes, MTMSN={mt_id}). Leyendo contenido...")
                    rt = send(ser, 'AT+SBDRT', 3.0)
                    payload = extract_sbdrt_payload(rt)
                    print("Contenido MT:\n" + payload + "\n")
                    append_logs(payload, sbd)
                else:
                    print("No hay mensajes pendientes.")

                time.sleep(POLL_SECONDS)
            else:
                print("Esperando signal>=2")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nSaliendo…")
