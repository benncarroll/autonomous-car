#!/usr/bin/env python

import RPi.GPIO as GPIO
import time
import signal

## Servo GPIO Setup
GPIO.cleanup()
servopin = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(servopin, GPIO.OUT, initial=False)
p = GPIO.PWM(servopin,50)
p.start(0)

## Define servoSet function
def setServoPosition(a):
    p.ChangeDutyCycle(a)
    return;

def checkFloat(a):
    try:
        a = a+1
        return True
    except TypeError:
        return False

repeatNum = 0

## Begin looping decision maker
try:
    while True:
        direction = input("Which direction do you want to go? ")
        if direction == "left":
            position = 9.9
        elif direction == "a":
            position = 9.9
        elif direction == "right":
            position = 4.9
        elif direction == "d":
            position = 4.9
        elif direction == "middle":
            position = 7.4
        elif direction == "s":
            position = 7.4
        elif checkFloat(direction):
            if float(direction) < 11:
                if float(direction) > 4:
                    position = float(direction)
        else:
            print("Invalid response.")
            if repeatNum < 1:
                position = 7.4
                print("Value has been set to middle.")
            else:
                print("Last valid response of " + str(position) + " will be used.")
        print("Variable given: " + direction + ". Interpreted as: " + str(position))

        p.start(0)
        setServoPosition(position)
        repeatNum += 1

## Clean up GPIO
except KeyboardInterrupt:
    time.sleep(.2)
    GPIO.cleanup()
    print()

# time.sleep(.2)
# GPIO.cleanup()
