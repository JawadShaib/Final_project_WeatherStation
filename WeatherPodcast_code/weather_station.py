from gpiozero import Button
import time
import math

# import wind_dirction
import WindSpeed
import dht11
import bme280
import statistics
import board
import serial
import RPi.GPIO as GPIO
from WD import wind_direction

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


""" setting up the Serial"""

ser = serial.Serial(
    port="/dev/ttyS0",
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1,
)

ser.flushInput()
wind_count = 0  # count how many half rotations
radius_cm = 9.0  # Radius of your anemometer
BUCKET_SIZE = 0.2794
wind_interval = 5  # how often (secs) to sample speed.
interval = 5  # measurments  recorded every X seconds,60*X miinutes ......
CM_IN_A_KM = 10000.0
SECS_IN_A_HOUR = 3600
ADJUSTMENT = 1.18
rain_count = 0
gust = 0
reset_flag = 0
store_directions = []
store_speeds = []
zero = [0.0] * 6

"""when the interupt is activated count++"""


def bucket_tipped():
    global rain_count
    rain_count = rain_count + 1
    # print (rain_count * BUCKET_SIZE)


def reset_rainfall():
    global rain_count
    rain_count = 0


""" setting up the wind speed"""
wind_speed_idx = WindSpeed.wind_speed_sensor
wind_speed_idx.when_pressed = WindSpeed.spin

""" setting up  the rain sensor"""
rain_sensor = Button(6)
rain_sensor.when_pressed = bucket_tipped

""" setting the wind direction sensor"""
direction_sensor = wind_direction(0, "wind_direction.json")


def send_data(
    tempreture, humidity, pressure, wind_speed, wind_direction, wind_dir, rain_fall
):
    ser.write(
        str.encode(
            "temperature:"
            + str(tempreture)
            + " "
            + "Humidity:"
            + str(humidity)
            + " "
            + "pressure: "
            + str(pressure)
        )
    )
    ser.write(str.encode("wind_speed: " + str(wind_speed) + " "))
    ser.write(str.encode("wind_direction: " + str(wind_angle) + "-" + wind_dir + " "))
    ser.write(str.encode("water: " + str(rain_fall) + " "))
    time.sleep(0.5)


""" start measuring"""
while True:
    """reading from labview serial port in case there is reset or not"""
    reset = ser.readline().strip()
    start_time = time.time()

    while time.time() - start_time <= interval and not reset:
        wind_start_time = time.time()
        WindSpeed.reset_wind()
        store_directions.append(direction_sensor.get_value())
        final_speed = WindSpeed.calculate_speed(wind_interval)
        store_speeds.append(final_speed)

    if not reset:
        humidity, tempreture = dht11.read_dht11()
        pressure = round(bme280.read_bme280(), 2)
        """after we store the final speeds of the wind , we should calculate the average of the wind dirction and the mean of wind speed"""
        wind_speed = round(statistics.mean(store_speeds), 3)
        wind_angle, wind_dir = direction_sensor.get_dir()
        wind_dirction_avg = direction_sensor.get_average(store_directions)
        rain_fall = 5  # count*bucket size
        """ sending data through serial port"""
        send_data(
            tempreture, humidity, pressure, wind_speed, wind_angle, wind_dir, rain_fall
        )
        """pritnig data for ediotr's feedback"""
        print("Tempreture---> ", tempreture)
        print("Humidity---> ", humidity)
        print("Pressure---> ", pressure)
        print("wind dirction---> ", wind_angle, wind_dir)
        print("wind speed---> ", wind_speed)
        print("\n")

    else:
        """when reset is on , setting up all the sesnsors to zero."""
        tempreture, humidity, pressure, wind_speed, wind_angle, rain_fall = zero
        wind_dir = "N"
        """ printing data for editor's feedback"""
        print("Tempreture---> ", tempreture)
        print("Humidity---> ", humidity)
        print("Pressure---> ", pressure)
        print("wind dirction---> ", wind_angle, wind_dir)
        print("wind speed---> ", wind_speed)
        print("\n")
        # time.sleep(3.5)#delay before reading
        """ sending data through serial port"""
        send_data(
            tempreture, humidity, pressure, wind_speed, wind_angle, wind_dir, rain_fall
        )
    """reseting the stored values in order to start measuring again at the start of the new interval"""
    # print("finsih time",time.time()-start_time)
    store_directions = []
    store_speeds = []
    reset_rainfall()


def send_temperature(tempreture):
    ser.write(str.encode("temperature:" + str(tempreture) + " "))


def send_humidity(humidity):
    ser.write(str.encode("Humidity:" + str(humidity) + " "))


def send_pressure(pressure):
    ser.write(str.encode("pressure: " + str(pressure) + " "))


def send_wind_speed(wind_speed):
    ser.write(str.encode("wind_speed: " + str(wind_speed) + " "))


def send_wind_direction(wind_direction, wind_dir):
    ser.write(str.encode("wind_direction: " + str(wind_angle) + "-" + wind_dir + " "))


def send_rainfall(rain_fall):
    ser.write(str.encode("water: " + str(rain_fall)) + " ")
