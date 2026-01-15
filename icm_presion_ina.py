#Patricio Jara Quiroz
#04/10/2024

# Lectura de sensores de presion (ABPMANT100PG2A3), IMU icm 29048 pimoroni, INA260


import smbus2
import time
import busio
import board
#import adafruit_ina260
import time
from icm20948 import ICM20948
import os
import csv
# Inicializacion del sensor de presion -----------------------------------
# Dirección I2C del sensor de presion:
I2C_ADDRESS = 0x28

# Inicializa el bus I2C para sensor de presion:
bus = smbus2.SMBus(1)

# Dirección del registro desde el cual leer (esto puede variar según el sensor) para sensor de presion
REGISTER_ADDRESS = 0x00  # Ajustar si es necesario

# Parámetros del sensor
OUTPUT_MIN = 0       # Mínimo valor digital (0 para 12 bits)
OUTPUT_MAX = 4095    # Máximo valor digital (12 bits: 2^12 - 1)
PRESSURE_MIN = 0.0   # Presión mínima en psi
PRESSURE_MAX = 100.0 # Presión máxima en psi

# La función read_pressure() lee al sensor en bits y entrega la presion en psi.
def read_pressure(): 
    # Lee 2 bytes de datos del sensor
    data = bus.read_i2c_block_data(I2C_ADDRESS, REGISTER_ADDRESS, 2)

    # Combina los dos bytes en un valor de 12 bits
    value = ((data[0] << 8) | data[1]) >> 4  # Desplazamos 4 bits para obtener los 12 bits válidos

    # Convierte el valor crudo de 12 bits a presión en psi
    pressure = ((value - OUTPUT_MIN) / (OUTPUT_MAX - OUTPUT_MIN)) * (PRESSURE_MAX - PRESSURE_MIN) + PRESSURE_MIN

    return pressure
print("Sensor de presión inciado")
# ------------------------ Fin inicialización sensor de presion --------------------

# Inicialización Sensor IN260:

#i2c = busio.I2C(board.SCL, board.SDA)
#ina260 = adafruit_ina260.INA260(i2c)
#print("Sensor INA260 inciado")

# ------------------------ Fin inicialización sensor INA260--------------------

# Inicalización IMU:--------------------------------------------------------------

imu = ICM20948()
imu._addr = 0x69      # cambiamos la dirección I2C manualmente

print("Sensor IMU iniciado")

# ------------------------ Fin inicialización sensor IMU--------------------





# Comienza la lectura de datos:---------------------------------


def create_csv_with_incremented_name(base_name):
    # Determina el nombre base y la extensión
    base = base_name.rsplit('.', 1)[0]
    extension = base_name.split('.')[-1]

    # Inicia el contador en 0
    index = 0
    current_file_name = f"{base}_{index}.{extension}"

    # Busca el nombre de archivo disponible incrementando el índice
    while os.path.exists(current_file_name):
        index += 1
        current_file_name = f"{base}_{index}.{extension}"
    
    
    # Capturar el tiempo inicial
    tiempo_inicial = time.time()
    
    # Abrir archivo CSV en modo de escritura con el nombre final
    with open(current_file_name, mode='w', newline='') as file:
        writer = csv.writer(file)
        print("Creando archivo csv")
        # Escribir la cabecera del CSV
        writer.writerow(["Time","gx", "gy", "gz", "mx", "my", "mz", "ax", "ay", "az","pressure","voltage","current","power"])
        print("Leyendo datos ...")
        try:

            while True:
                tiempo_actual = time.time() # Lee tiempo actual
                tiempo_transcurrido = (tiempo_actual - tiempo_inicial) * 1000  # Tiempo transcurrido en milisegundos
                
                # Lectura de IMU
                mx, my, mz = imu.read_magnetometer_data()
                ax, ay, az, gx, gy, gz = imu.read_accelerometer_gyro_data()   
                # Fin lectura IMU

                # Leer la presión del sensor
                pressure =0# read_pressure() # psi
                # Fin lectura presion

                writer.writerow([tiempo_transcurrido, gx, gy, gz, mx, my, mz, ax, ay, az, pressure,0,0,0])#  , ina260.voltage, ina260.current, ina260.power])  # Escribir datos al archivo CSV
                print("g ", "%.2f" % gx, "%.2f" % gy, "%.2f" % gz, "  m: " ,"%.2f" % mx, "%.2f" % my, "%.2f" % mz, "  a: ", "%.2f" % ax, "%.2f" % ay, "%.2f" % az, "  p: ","%.2f" % pressure)# , "  INA: ","%.2f" % ina260.voltage, "%.2f" % ina260.current, "%.2f" % ina260.power)
                time.sleep(0.01)



        except KeyboardInterrupt:
            print("Lectura interrumpida")
        finally:
            bus.close()

create_csv_with_incremented_name('data_icm/datos_ICM.csv')



# Fin del programa
