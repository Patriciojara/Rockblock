# Autor: Patricio Jara Quiroz
# Fecha: 08-10-2025
# Descripción: lee y envia a ubicacion del gps por Rockblock.

import subprocess
import pandas as pd
import csv

read_csv = pd.read_csv('ubicacion.csv')

date = read_csv['date'].iloc[-1]
latitud = read_csv['latitud'].iloc[-1]
longitud = read_csv['longitud'].iloc[-1]
altitud = read_csv['altitud'].iloc[-1]
velocidad = read_csv['velocidad'].iloc[-1]


mensaje = "Da:{}, La: {}, Lo: {}, A: {:.2} m, Vel: {:.2f} km/h".format(date, float(latitud), longitud, float(altitud), float(velocidad))

ubicacion = subprocess.Popen(["python3", "envia_entrada.py", mensaje], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

# Mostrar salida en tiempo real
for line in ubicacion.stdout:
    print(line, end='')

# Mostrar errores en tiempo real
for err in ubicacion.stderr:
    print(err, end='')
