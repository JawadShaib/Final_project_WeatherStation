import Adafruit_DHT
import time
import serial

ser = serial.Serial(
    port="/dev/ttyS0",
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1,
)

DHT_sensor = Adafruit_DHT.DHT11
DHT_PIN = 4


def read_dht11():
    while True:
        humidity, temperature = Adafruit_DHT.read(DHT_sensor, DHT_PIN)
        if humidity is not None and temperature is not None:
            return humidity, temperature
