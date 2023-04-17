from gpiozero import Button
import math
import time
import statistics


store_speeds = []
CM_IN_A_KM = 100000.0
SECS_IN_AN_HOUR = 3600
ADJUSTMENT = 1.18


wind_count = 0  # counts how many half -rotaions
radius_cm = 9.0  # Radious of your anemometer
wind_interval = 5  # How often (Secs) to report spee


# function that will be run whenever the pin is activated by a spin of the anemometer.
# every half rotations, add 1 to count


def spin():
    global wind_count  # declare as a global so that it can be accessed from withon the function.
    wind_count = wind_count + 1


#     print("spin" + str(wind_count))


# calculate the wind speed
def calculate_speed(time_sec):
    global wind_count
    circumference_cm = (2 * math.pi) * radius_cm
    rotations = wind_count / 2.0
    # calculate distance traveleed by a cup in cm
    dist_km = (circumference_cm * rotations) / CM_IN_A_KM

    km_per_sec = dist_km / time_sec
    km_per_hour = km_per_sec * SECS_IN_AN_HOUR

    return km_per_hour * ADJUSTMENT


# it will be useful to be able to reset your wind_count variable to zero to measure in every new interval
# so add a function that does that now:
def reset_wind():
    global wind_count
    wind_count = 0


# GPIOzero’s Button functions and set up a Button on GPIO 5
wind_speed_sensor = Button(5)
wind_speed_sensor.when_pressed = spin
