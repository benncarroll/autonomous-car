#!/usr/bin/env python

import RPi.GPIO as GPIO
import time
import curses

# Ensure safe exit
import atexit
atexit.register(GPIO.cleanup)

class u_sensor(object):
    """docstring for u_sensor."""

    def __init__(self, trigger_pin, echo_pin, direction):
        self.trigger_pin = trigger_pin
        self.echo_pin = echo_pin
        self.dir = direction

        GPIO.setup(trigger_pin, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(echo_pin, GPIO.IN)
        time.sleep(0.5)

    def get_distance(self):
        GPIO.output(self.trigger_pin, GPIO.HIGH)
        time.sleep(0.000015)
        GPIO.output(self.trigger_pin, GPIO.LOW)
        while not GPIO.input(self.echo_pin):
            pass
        t1 = time.time()
        while GPIO.input(self.echo_pin):
            pass
        t2 = time.time()
        t3 = (t2 - t1) * 340 / 2

        result = float('%.2f' % (t3))

        if result > 20:
            result = 0.3
            # result = self.get_distance()

        return result

    def __str__(self):
        return direction.capitalize()

#                 front, left, right, back
ultrasonic_list = [u_sensor(29, 31, "front"), u_sensor(35,37, "left"), u_sensor(38,40, "right")]

def myround(x, base=5):
    return int(base * round(float(x)/base))

def main(screen):
    curses.curs_set(0)
    screen.timeout(200)

    while True:

        bars = list()

        for sensor in ultrasonic_list:
            dist = sensor.get_distance()
            bars.append((myround(dist)/5))








        time.sleep(.1)
