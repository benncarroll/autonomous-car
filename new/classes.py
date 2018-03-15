
#
# Copyright 2017, Ben Carroll, All rights reserved.
#
# Repo:     www.github.com/benncarroll/autonomous-car
# Website:  www.benncarroll.tech
#

import RPi.GPIO as GPIO
import time

# GPIO init
GPIO.setmode(GPIO.BOARD)

class u_sensor(object):
    """docstring for u_sensor."""

    def __init__(self, trigger_pin, echo_pin):
        self.trigger_pin = trigger_pin
        self.echo_pin = echo_pin
        GPIO.setup(trigger_pin, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(echo_pin, GPIO.IN)
        time.sleep(0.5)

    def get_distance(self):
        GPIO.output(self.trigger_pin, GPIO.HIGH)
        time.sleep(0.000015)
        GPIO.output(self.trigger_pin, GPIO.LOW)
        while not (GPIO.input(self.echo_pin)):
            pass
        t1 = time.time()
        while GPIO.input(self.echo_pin):
            pass
        t2 = time.time()
        t3 = (t2 - t1) * 340 / 2

        result = float('%.2f' % (t3))

        # if result > 20:
        #     result = 0.3
        #     result = self.get_distance()

        GPIO.output(self.trigger_pin, GPIO.LOW)


        return result


class log_data_class():
    def __init__(self):
        self.dt = time.strftime("%Y%m%d-%H%M%S")
        self.fs = None
        self.ls = None
        self.rs = None
        self.si = None
        self.ti = None
