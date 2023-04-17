from gpiozero import MCP3008
import time
import math

# allow SPI in raspberry: RPI configuration-> interface-> SPI=on
# reading the values from mcp3008
adc = MCP3008(channel=0)
count = 0
wind_interval = 5
data = []
values = []

# voltages will be the keys and the corresponding angles will be the values.
volts = {
    0.4: 0.0,
    1.4: 22.5,
    1.2: 45.5,
    2.8: 67.5,
    2.7: 90.0,
    2.9: 112.5,
    2.2: 135.0,
    2.5: 157.5,
    1.8: 180.0,
    2.0: 202.5,
    0.7: 225.0,
    0.8: 247.5,
    0.1: 270.0,
    0.3: 292.5,
    0.2: 315.0,
    0.6: 337.5,
}


dirctions = {
    0.0: "N",
    22.5: "NNE",
    45.5: "NE",
    67.5: "ENE",
    90.0: "E",
    112.5: "ENE",
    135.0: "SE",
    157.5: "SSE",
    180.0: "S",
    202.5: "SSW",
    225.0: "SW",
    247.5: "WSW",
    270.0: "W",
    292.5: "WNW",
    315.0: "NW:",
    337.5: "NNW",
}


def get_value():
    data = []
    print("measuring wind dirction for %d seconds..." % wind_interval)

    start_time = time.time()

    while time.time() - start_time <= wind_interval:
        wind = round(adc.value * 3.3, 1)

        if wind in volts:
            data.append(volts[wind])

    return round(get_average(data), 1)


def get_average(angles):
    sin_sum = 0.0
    cos_sum = 0.0

    for angle in angles:
        r = math.radians(angle)
        sin_sum += math.sin(r)
        cos_sum += math.cos(r)

    flen = float(len(angles))
    if not flen:
        return 0
    s = sin_sum / flen
    c = cos_sum / flen
    arc = math.degrees(math.atan(s / c))
    average = 0.0

    if s > 0 and c > 0:
        average = arc
    elif c < 0:
        average = arc + 180
    elif s < 0 and c > 0:
        average = arc + 360

    return 0.0 if average == 360 else average


#
# try:
#
#     while True:
#
#         wind=round(adc.value*3.3,1)
# #         print(wind)
# #         time.sleep(2)
#
#         if wind in volts and volts[wind] not in data:
#
#             data.append(volts[wind])
#
# except KeyboardInterrupt:
#     print(" keyboard interupt")
#     print(data)
#
#
#


while True:
    wind = round(adc.value * 3.3, 1)
    if wind not in values:
        values.append(wind)
        print(wind)
