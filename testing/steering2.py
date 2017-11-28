#!/usr/bin/python

##import Adafruit_PCA9685
import RPi.GPIO as GPIO
import time
import curses

escpin = 11
GPIO.setmode(GPIO.BOARD)
GPIO.setup(escpin, GPIO.OUT)
pwm = GPIO.PWM(escpin, 50)
pwm.start(0)

screen = curses.initscr()
# turn off input echoing
curses.noecho()
# respond to keys immediately (don't wait for enter)
curses.cbreak()
# map arrow keys to special values
screen.keypad(True)

done = False
numbmax = 4
numbmin = 0
numb = 2
steering_list = [9.0, 8.0, 7.5, 7.0, 6.0]

try:
    while not done:
        char = screen.getch()
        if char == ord('q'):
            done = True

        else:
            if char == curses.KEY_UP:
                if numb < numbmax:
                    numb += 1
                screen.clear()
                screen.addstr(0,0,"keyup")
            elif char == curses.KEY_DOWN:
                if numb > numbmin:
                    numb -= 1
                screen.clear()
                screen.addstr(0,0,"keydown")
            if char == curses.KEY_RIGHT:
                if numb < numbmax:
                    numb += 1
                screen.clear()
                screen.addstr(0,0,"keyup")
            elif char == curses.KEY_LEFT:
                if numb > numbmin:
                    numb -= 1
                screen.clear()
                screen.addstr(0,0,"keydown")

            end = steering_list[numb]

            if char == 10:
                screen.addstr(0,0,"custom...")
                screen.refresh()
                custom = ""
                c = screen.getch()
                while c != 10:
                    custom += chr(c)
                    screen.addstr(2,0,"custom: " + custom)
                    screen.refresh()
                    c = screen.getch()
                screen.clear()
                screen.addstr(0,0,"custom: " + custom)
                end = float(custom)

        screen.addstr(1,0,"numb: {}".format(end))
        pwm.ChangeDutyCycle(end)

finally:
    # shut down cleanly
    curses.nocbreak()
    screen.keypad(0)
    curses.echo()
    curses.endwin()
    print(numb)  # !/usr/bin/env python

"""import RPi.GPIO as GPIO
import time
import signal

# Servo GPIO Setup
GPIO.cleanup()
servopin = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(servopin, GPIO.OUT, initial=False)
p = GPIO.PWM(servopin, 50)
p.start(0)

# Define servoSet function


def setServoPosition(a):
    p.ChangeDutyCycle(a)
    return


def checkFloat(a):
    try:
        a = a + 1
        return True
    except TypeError:
        return False


# Begin looping decision maker
# try:
#     for _ in range(eval(input("How many times should we repeat? "))):
#         direction = input("How fast do you want to go? ")

# if direction == "left":
##            position = 10
# elif direction == "a":
##            position = 10
# elif direction == "right":
##            position = 5
# elif direction == "d":
##            position = 5
# elif direction == "middle":
##            position = 7.5
# elif direction == "s":
##            position = 7.5
# elif checkFloat(direction):
# if float(direction) < 11:
# if float(direction) > 4:
##                    position = float(direction)
# else:
# print "Invalid response."
# if _ < 1:
##                position = 7.5
# print "Value has been set to middle."
# else:
# print "Last valid response of " + str(position) + " will be used."
# print "Variable given: " + direction + ". Interpreted as: " + str(position)

        # position = float(direction)
        #
        # setServoPosition(position)

# Clean up GPIO
except KeyboardInterrupt:
    time.sleep(.2)
    GPIO.cleanup()


time.sleep(.2)
GPIO.cleanup()
"""
