#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monitor continuo de señal RockBLOCK (AT+CSQ).
- Muestra nivel de señal 0–5 con barras y comentario.
- Guarda log opcional en CSV.
- Reintenta si no hay respuesta.
"""

import argparse, csv, sys, time, re
from datetime import datetime
import serial

CSQ_RE = re.compile(r"\+CSQ:\s*(\d+)")

LEVEL_HINT = {
    0: "sin señal",
    1: "muy débil (marginal)",
    2: "usable al aire libre",
    3: "buena",
    4: "muy buena",
    5: "excelente"
}

def send_at(ser: serial.Serial, cmd: str, timeout=3.0):
    """Envía un AT y devuelve (ok, líneas). ok=True si ve 'OK'."""
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    ser.write((cmd.strip() + "\r").encode("ascii"))
    ser.flush()

    deadline = time.time() + timeout
    lines = []
    ok, err = False, False

    while time.time() < deadline:
        if ser.in_waiting:
            line = ser.readline().decode(errors="replace").strip()
            if line:
                lines.append(line)
                if line == "OK":
                    ok = True
                    break
                if line.startswith("ERROR"):
                    err = True
                    break
        else:
            time.sleep(0.02)

    return (ok and not err), lines

def parse_csq(lines):
    """Extrae valor CSQ (0-5) de las líneas devueltas."""
    for ln in lines:
        m = CSQ_RE.search(ln)
        if m:
            try:
                return int(m.group(1))
            except ValueError:
                return None
    return None

def print_line(ts, csq, raw):
    bars = "█" * (csq if csq is not None else 0)
    spaces = " " * (5 - (csq if csq is not None else 0))
    level = csq if csq is not None else "-"
    hint = LEVEL_HINT.get(csq, "n/d")
    print(f"{ts}  CSQ {level}/5  [{bars}{spaces}]  {hint}")

def main():
    ap = argparse.ArgumentParser(description="Monitor continuo de señal RockBLOCK (AT+CSQ).")
    ap.add_argument("--port", "-p", default="/dev/serial0",
                    help="Puerto serie (ej. /dev/ttyUSB0, /dev/serial0, COM3)")
    ap.add_argument("--baud", "-b", type=int, default=19200,
                    help="Baudios (por defecto 19200)")
    ap.add_argument("--poll", "-t", type=float, default=5.0,
                    help="Periodo de muestreo en segundos (p.ej. 2, 5, 10)")
    ap.add_argument("--csv", help="Ruta para guardar CSV (timestamp,csq,raw)")
    ap.add_argument("--once", action="store_true", help="Mide una sola vez y sale")
    ap.add_argument("--init-wait", type=float, default=1.5,
                    help="Espera tras abrir el puerto (segundos)")
    args = ap.parse_args()

    try:
        ser = serial.Serial(
            port=args.port,
            baudrate=args.baud,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=0.2,          # lectura no bloqueante corta
            xonxoff=False,
            rtscts=False,
            dsrdtr=False
        )
    except Exception as e:
        print(f"[ERR] No se pudo abrir {args.port}: {e}", file=sys.stderr)
        sys.exit(1)

    time.sleep(args.init_wait)

    # Comprueba que responde a AT
    ok, lines = send_at(ser, "AT", timeout=1.5)
    if not ok:
        print("[WARN] El módem no respondió 'OK' a AT. Verifica cableado/port/baudios.", file=sys.stderr)
        # No salimos: a veces despierta con el primer comando.

    csv_writer = None
    csv_fp = None
    if args.csv:
        csv_fp = open(args.csv, "a", newline="", encoding="utf-8")
        csv_writer = csv.writer(csv_fp)
        # Encabezado si el archivo está vacío
        if csv_fp.tell() == 0:
            csv_writer.writerow(["timestamp", "csq", "raw"])

    try:
        while True:
            ts = datetime.now().isoformat(timespec="seconds")
            ok, lines = send_at(ser, "AT+CSQ", timeout=2.5)
            csq = parse_csq(lines) if ok else None

            if csq is None and not ok:
                print(f"{ts}  CSQ -/5  [     ]  sin respuesta, reintentando...")
            else:
                print_line(ts, csq, lines)

            if csv_writer:
                csv_writer.writerow([ts, csq if csq is not None else "", " | ".join(lines)])
                csv_fp.flush()

            if args.once:
                break
            time.sleep(max(args.poll, 0.5))  # evita sobrecargar el módem
    except KeyboardInterrupt:
        print("\nSaliendo…")
    finally:
        if csv_fp:
            csv_fp.close()
        ser.close()

if __name__ == "__main__":
    main()
