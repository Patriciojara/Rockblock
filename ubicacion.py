import subprocess
import pandas as pd
import csv

read_csv = pd.read_csv('ubicacion.csv')

latitud = read_csv['latitud'][0]
longitud = read_csv['longitud'][0]
altitud = read_csv['altitud'][0]
velocidad = read_csv['velocidad'][0]


mensaje = "Latitud: {}, Longitud: {}, Altitud: {} m, Velocidad: {} km/h".format(latitud, longitud, altitud, velocidad)

ubicacion = subprocess.Popen(["python3", "envia_entrada.py", mensaje], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

# Mostrar salida en tiempo real
for line in ubicacion.stdout:
    print(line, end='')

# Mostrar errores en tiempo real
for err in ubicacion.stderr:
    print(err, end='')
