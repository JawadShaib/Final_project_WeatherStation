import board
import time
from adafruit_bme280 import basic as adafruit_bme280

# Create sensor object, using the board's default I2C bus.
# to detect the I2C address use sudo  i2cdetect -y 1 in terminal

i2c = board.I2C()  # uses board.SCL and board.SDA
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)

# change this to match the location's pressure (hPa) at sea level
bme280.sea_level_pressure = 1013.25


def read_bme280():
    while True:
        bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)

        if bme280.pressure is not None:
            return bme280.pressure
