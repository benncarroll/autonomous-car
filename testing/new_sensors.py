import RPi.GPIO as GPIO
import time

# Ensure safe exit
import atexit
atexit.register(GPIO.cleanup)


pins_bcm = [17, 27, 22, 23]
pins_board = [11, 13, 15, 16]
pins_named = [1, 2, 3, 4]

GPIO.setmode(GPIO.BCM)

for i, pin in enumerate(pins_bcm):
    GPIO.setup(pin, GPIO.IN)

while True:

    s = False

    for i, pin in enumerate(pins_bcm):
        if GPIO.input(pin) == GPIO.LOW:
            print("Sensor {} triggered.".format(pins_named[i]))
            s = True

    if not s:
        print("Nothing.")

    time.sleep(0.5)
