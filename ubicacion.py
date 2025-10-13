import subprocess
import pandas as pd
import csv

read_csv = pd.read_csv('ubicacion.csv')

latitud = read_csv['latitud'][0]
longitud = read_csv['longitud'][0]
altitud = read_csv['altitud'][0]
velocidad = read_csv['velocidad'][0]


mensaje = "Latitud: {}, Longitud: {}, Altitud: {} m, Velocidad: {} km/h".format(latitud, longitud, altitud, velocidad)

ubicacion = subprocess.run(["python3", "envia_entrada.py", mensaje],capture_output=True, text=True)

print("Salida del script:")
print(ubicacion.stdout)

print("Errores (si hubo):")
print(ubicacion.stderr)
