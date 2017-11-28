#!/usr/bin/env python

import RPi.GPIO as GPIO
import time
import curses

## Scren setup
scr = curses.initscr()
scr.addstr(0,0, "Averaged Distance: ")
scr.addstr(1,0, "Raw Distance: ")
scr.addstr(2,0, "Changed?")

## Servo GPIO Setup
servopin = 11
GPIO.setmode(GPIO.BOARD)
GPIO.setup(servopin, GPIO.OUT, initial=False)
p = GPIO.PWM(servopin,50)
p.start(0)

## Ultrasonic GPIO Setup
GPIO.setmode(GPIO.BOARD)
GPIO.setup(16,GPIO.OUT,initial=GPIO.LOW)
GPIO.setup(18,GPIO.IN)
time.sleep(2)
turnDist = 1 ## In metres

## Define servoSet function
def setServoPosition(a):
    p.ChangeDutyCycle(a)
    return;

## Define check Distance function
def checkDist():
    GPIO.output(16, GPIO.HIGH)
    time.sleep(0.000015)
    GPIO.output(16, GPIO.LOW)
    while not GPIO.input(18):
            pass
    t1 = time.time()
    while GPIO.input(18):
            pass
    t2 = time.time()
    t3 = (t2-t1)*340/2
    return '%.2f'%(t3)
##    return float('%.2f'%(t3))

def checkAverageDist():
    result1 = checkDist()
    time.sleep(0.01)
    result2 = checkDist()
    time.sleep(0.01)
    result3 = checkDist()

    resultf = (result1 + result2 + result3) / 3

    return '%.2f'%resultf

## Begin looping decision maker
try:
    lastUsedDir = 7.5

    while True:
        currentDist = checkDist()
        rawDist = checkDist()
        scr.addstr(0,20, currentDist + "m  ")
        scr.addstr(1,20, str(rawDist) + "m  ")
        scr.refresh()
##        print (currentDist + "m", end="\r", flush=True)
        currentDist = float(currentDist)
        if currentDist < turnDist and (lastUsedDir != 5):
            position = 5
            changed = "Yes"
            setServoPosition(position)

        elif currentDist > turnDist and  (lastUsedDir != 7.5):
            position = 7.5
            changed = "Yes"
            setServoPosition(position)

        else:
            position = lastUsedDir
            changed = "No "

        scr.addstr(2,20, changed)
        lastUsedDir = position
        time.sleep(0.2)


## Clean up GPIO
except KeyboardInterrupt:
    time.sleep(.2)
    GPIO.cleanup()
    curses.endwin()
