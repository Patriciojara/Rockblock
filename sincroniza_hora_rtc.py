import smbus
import time
import datetime
import os

# Dirección I2C del RTC DS3231
RTC_ADDRESS = 0x68

# Función para leer el valor de un registro del RTC
def read_byte(reg):
    bus = smbus.SMBus(1)
    return bus.read_byte_data(RTC_ADDRESS, reg)

# Función para convertir los valores de BCD a decimal
def bcd_to_decimal(bcd):
    return (bcd & 0xF) + ((bcd >> 4) * 10)

# Función para obtener la hora del RTC
def read_time():
    bus = smbus.SMBus(1)
    
    # Leer los registros del RTC (hora, minuto, segundo, día, mes, año)
    second = bcd_to_decimal(read_byte(0x00))
    minute = bcd_to_decimal(read_byte(0x01))
    hour = bcd_to_decimal(read_byte(0x02))
    day = bcd_to_decimal(read_byte(0x04))
    month = bcd_to_decimal(read_byte(0x05))
    year = bcd_to_decimal(read_byte(0x06)) + 2000
    
    # Crear un objeto datetime con la hora obtenida
    rtc_time = datetime.datetime(year, month, day, hour, minute, second)
    
    return rtc_time

# Función para sincronizar la hora del sistema con el RTC
def sync_system_time():
    rtc_time = read_time()
    # Establecer la hora del sistema (usando el comando `sudo date`)
    date_command = rtc_time.strftime("sudo date -s \"%Y-%m-%d %H:%M:%S\"")
    os.system(date_command)
    print(f"Hora sincronizada con el RTC: {rtc_time}")

if __name__ == '__main__':
    sync_system_time()
