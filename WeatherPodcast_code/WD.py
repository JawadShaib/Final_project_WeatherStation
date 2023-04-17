#!/usr/bin/python3
import json
import math
import os
from gpiozero import MCP3008
from statistics import mean
import time


class wind_direction(object):
    angles = {
        0.0: "N",
        22.5: "NNE",
        45.0: "NE",
        67.5: "ENE",
        90.0: "E",
        112.5: "ESE",
        135.0: "SE",
        157.5: "SSE",
        180.0: "S",
        202.5: "SSW",
        225.0: "SW",
        247.5: "WSW",
        270.0: "W",
        292.5: "WNW",
        315.0: "NW",
        337.5: "NNW",
    }

    def __init__(self, adc_channel=0, config_file=None):
        self.adc_channel = adc_channel
        self.adc = MCP3008(self.adc_channel)

        config_file_path = r"./WeatherPodcast_code/wind_dirction.json"

        with open(config_file_path, "r") as f:
            self.config = json.load(f)

        vin = self.config["vin"]
        vdivider = self.config["vdivider"]
        self.max = 2.9
        self.vref = 3.3

        for dir in self.config["directions"]:
            dir["vout"] = round(self.calculate_vout(vdivider, dir["ohms"], vin), 3)
            # dir["adc"] = round(self.max * (dir["vout"] / self.vref),1)

        self.sorted_by_adc = sorted(
            self.config["directions"], key=lambda x: x["adc"]
        )  # sorting win dirctions by adc value .
        # enumerate(sorted_by_adc)

        for index, dir in enumerate(self.sorted_by_adc):
            if index > 0:
                below = self.sorted_by_adc[index - 1]
                delta = (dir["adc"] - below["adc"]) / 2.0
                dir["adcmin"] = round(dir["adc"] - delta, 3)
            else:
                dir["adcmin"] = 0.1

            if index < (len(self.sorted_by_adc) - 1):
                above = self.sorted_by_adc[index + 1]
                delta = (above["adc"] - dir["adc"]) / 2.0
                dir["adcmax"] = round(dir["adc"] + delta, 3)
            else:
                dir["adcmax"] = self.max
        print(self.sorted_by_adc)

    def calculate_vout(self, ra, rb, vin):  # Ohm's law resistive divider calculation
        return (float(rb) / float(ra + rb)) * float(vin)

    def get_angle(self, adc_value):
        angle = None
        for dir in self.sorted_by_adc:
            if (
                adc_value > 0
                and adc_value >= dir["adcmin"]
                and adc_value <= dir["adcmax"]
            ):
                angle = dir["angle"]
                break

        return angle

    def get_dir(self):
        adc_value = round(self.adc.value * 3.3, 1)
        angle = None
        for dir in self.sorted_by_adc:
            if (
                adc_value > 0
                and adc_value >= dir["adcmin"]
                and adc_value <= dir["adcmax"]
            ):
                angle = dir["angle"]
                return angle, self.angles[angle]

    def get_value(self, length=5):
        data = []
        start_time = time.time()

        while time.time() - start_time <= length:
            adc_value = round(self.adc.value * 3.3, 1)
            angle = self.get_angle(adc_value)

            if angle is not None:  # keep only good measurements
                data.append(angle)

        return round(self.get_average(data), 1)

    def get_average(self, angles):
        """
        Consider the following three angles as an example: 10, 20, and 30
        degrees. Intuitively, calculating the mean would involve adding these
        three angles together and dividing by 3, in this case indeed resulting
        in a correct mean angle of 20 degrees. By rotating this system
        anticlockwise through 15 degrees the three angles become 355 degrees,
        5 degrees and 15 degrees. The naive mean is now 125 degrees, which is
        the wrong answer, as it should be 5 degrees.
        """

        # http://en.wikipedia.org/wiki/Directional_statistics

        sin_sum = 0.0
        cos_sum = 0.0

        for angle in angles:
            r = math.radians(angle)
            sin_sum += math.sin(r)
            cos_sum += math.cos(r)

        flen = float(len(angles))
        if not flen:
            return 0.0
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
