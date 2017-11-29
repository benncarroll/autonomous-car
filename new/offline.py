import RPi.GPIO as GPIO
import time

# Ensure safe exit
import atexit
atexit.register(GPIO.cleanup)

on_button = 32
led_pin = 7

GPIO.setmode(GPIO.BOARD)
GPIO.setup(on_button, GPIO.IN)
GPIO.setup(led_pin, GPIO.OUT, initial=False)

for i in range(5):
    while GPIO.input(on_button) == GPIO.LOW:
        time.sleep(0.1)
        pass
    time.sleep(1)

GPIO.output(led_pin, GPIO.HIGH)
