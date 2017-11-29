#!/usr/bin/env python

import RPi.GPIO as GPIO
import time
import curses
import classes

import csv
import os

# Ensure safe exit
import atexit
atexit.register(GPIO.cleanup)

# Pin variables (physical location)
sync_button_pin = 32
throttle_pin = 13
steering_pin = 11
ultrasonic_list = [classes.u_sensor(29, 31), classes.u_sensor(35, 37), classes.u_sensor(38, 40)]  # front, left, right


# Setup logging
timestr = time.strftime("%Y%m%d-%H%M%S")
log_path = "/home/pi/car/logs/auto - {}.csv".format(timestr)

if not os.path.isfile(log_path):
    csv_launcher = open(log_path, 'w').close()

csvfile = open(log_path, 'w', newline='')
logger = csv.writer(csvfile, delimiter=',',
                    quotechar='|', quoting=csv.QUOTE_MINIMAL)

# Header
logger.writerow(["Date/Time",
                 "Front Sensor Dist",
                 "Left Sensor Dist",
                 "Right Sensor Dist",
                 "Steering Index",
                 "Throttle Index"
                 ])


# GPIO init
GPIO.setmode(GPIO.BOARD)

# Sync button setup
GPIO.setup(sync_button_pin, GPIO.IN)

# Steering servo GPIO Setup
GPIO.setup(steering_pin, GPIO.OUT, initial=False)
steering_servo = GPIO.PWM(steering_pin, 50)
steering_servo.start(0)

# Throttle GPIO Setup
GPIO.setup(throttle_pin, GPIO.OUT, initial=False)
throttle_servo = GPIO.PWM(throttle_pin, 50)

#                 close, far
avoid_distances = [0.8, 1.5]

log_data = classes.log_data_class()

# Vars
steering_bar = ['←', '\\', '|', '/', '→']
steering_list = [9.0, 8.0, 7.5, 7.0, 6.0]
steering_index = 2
prev_s_index = 2

throttle_bar = ['R', 'N', '1', '2', '3']
throttle_list = [6.5, 7.5, 8.1, 8.15, 8.1]
# throttle_list = [6.2, 7.5, 8, 8.1, 8.2]
throttle_index = 1
prev_t_index = 1


def write(screen, string, row, align='center', bar=False):
    dims = screen.getmaxyx()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_GREEN)

    if row == "last":
        row = dims[0] - 1
    elif row == "first":
        row = 0

    if align == 'right':
        column = dims[1] - len(string) - 1
    elif align == 'left':
        column = 0
    else:
        column = dims[1] // 2 - len(string) // 2

    if bar:
        screen.addstr(row, column, string, curses.color_pair(2))
    else:
        screen.addstr(row, column, string)

    for i, char in enumerate(string):
        for bar, index, line in [[steering_bar, steering_index, 8], [throttle_bar, throttle_index, 11]]:
            if char == bar[index] and row == line:
                screen.addstr(row, column + i, char, curses.color_pair(1))

    screen.refresh()


def sync_esc():

    print("\n" * 2)
    print("Please turn the car off and then on again.\nAfter it's first beep, press the button.")

    # Wait for button press
    while GPIO.input(sync_button_pin) == GPIO.LOW:
        time.sleep(0.1)

    print("Syncing...")

    throttle_servo.start(7.5)
    time.sleep(0.25)
    throttle_servo.ChangeDutyCycle(10)
    time.sleep(2)
    throttle_servo.ChangeDutyCycle(7.5)
    time.sleep(0.25)

    print("Sync process completed. Loading dashboard...")
    time.sleep(0.8)
    print("\n" * 2)


def servoSet():
    global prev_t_index, prev_s_index, throttle_index, steering_index

    # prev_?_index is used so that the pulse width does not have
    # to be reset every cycle, possibly cutting pulses short.

    if prev_s_index != steering_index:

        steering_servo.ChangeDutyCycle(steering_list[steering_index])

        prev_s_index = steering_index

    # prev_t_index is also used to make sure the special case to engage
    # reverse is not triggered every single time an update is performed.
    if prev_t_index != throttle_index:
        if throttle_index > 0:
            throttle_servo.ChangeDutyCycle(throttle_list[throttle_index])
        elif throttle_index == 0 and prev_t_index != 0:
            # Special case for reversing, in which the 'reverse' mode
            # acts as a brake if coming straight from accelerate mode
            # and only reverse on second entry into 'reverse' mode.
            throttle_servo.ChangeDutyCycle(throttle_list[0])
            time.sleep(0.2)
            throttle_servo.ChangeDutyCycle(throttle_list[1])
            time.sleep(0.2)
            throttle_servo.ChangeDutyCycle(throttle_list[0])
        prev_t_index = throttle_index

    log_data.dt = time.strftime("%Y%m%d-%H%M%S")
    log_data.si = steering_index
    log_data.ti = throttle_index


def end(screen):
    # Stop PWM's
    throttle_servo.stop()
    steering_servo.stop()
    # Make sure car is turned off.
    screen.clear()
    write(screen, "Before quitting, please turn off the car.", 5)
    write(screen, "After doing so, press any key to end.", 6)
    screen.timeout(-1)
    screen.getch()

    # Close log file
    csvfile.close()


def main(screen):

    # global prev_t_index,
    global steering_bar, steering_list, steering_index
    global throttle_bar, throttle_list, throttle_index

    curses.curs_set(0)
    screen.timeout(100)

    write(screen, "▁▂▃▄▅▆▇█ Ben Carroll's Automagic Car █▇▆▅▄▃▂▁", 2)
    write(screen, "This script automatically controls the the car,", 4)
    write(screen, "and does not require user input.", 5)
    write(screen, "Current Steering Position", 7)
    write(screen, "Current Throttle Level", 10)

    write(screen, "Designed and Programmed by Ben Carroll", "last", "right")

    char = 0
    paused = False
    pause_line_written = False
    loopNum = 0

    while True:

        # Pause
        if char == ord('p'):
            if paused:
                paused = False
                write(screen, "         ", 16)
            else:
                steering_index = 2
                throttle_index = 1
                write(screen, " PAUSED ", 16, bar=True)
                paused = True

        # Quit
        if char == ord('q'):
            break

        if not paused:

            steering_index = 2
            throttle_index = 3

            # Get reading from sensor
            front_dist = ultrasonic_list[0].get_distance()
            left_dist = ultrasonic_list[1].get_distance()
            right_dist = ultrasonic_list[2].get_distance()

            smallest_dist = min(front_dist, left_dist, right_dist)

            # Check for further distance
            if smallest_dist <= avoid_distances[1]:

                if not throttle_index == 0:
                    if left_dist > right_dist:
                        steering_index = 0
                    else:
                        steering_index = 4
                throttle_index = 3

            # Check for closer distance
            if smallest_dist <= avoid_distances[0]:

                if not throttle_index == 0:
                    if left_dist > right_dist:
                        steering_index = 0
                    else:
                        steering_index = 4
                    throttle_index = 2

            # Reverse if closer than 30cm
            for sensor in ultrasonic_list:
                a = sensor.get_distance()
                if a <= 0.3 and a != 0.06:
                    throttle_index = 0
                    steering_index = {
                        0: 4,
                        1: 3,
                        2: 2,
                        3: 1,
                        4: 0
                    }[steering_index]

            # Straighten steering after finishing reversing
            if throttle_index > 0 and prev_t_index == 0:
                steering_index = 2

        servoSet()

        log_data.fs = front_dist
        log_data.ls = left_dist
        log_data.rs = right_dist

        if not paused:
            logger.writerow([
                log_data.dt, log_data.fs, log_data.ls, log_data.rs, log_data.si, log_data.ti
            ])
            pause_line_written = False
        else:
            if not pause_line_written:
                logger.writerow(log_data.dt)
                pause_line_written = True

        temp_s_bar = steering_bar
        s_overlay_char = temp_s_bar[steering_index]
        temp_t_bar = throttle_bar
        t_overlay_char = temp_t_bar[throttle_index]

        write(screen, ' ' + ' '.join(temp_s_bar) + ' ', 8, bar=True)
        write(screen, ' ' + ' '.join(temp_t_bar) + ' ', 11, bar=True)
        write(screen, "  Raw Throttle: {} - Raw Steering: {}".format(
            throttle_list[throttle_index], steering_list[steering_index]), 14)
        write(screen, "  {} || {} || {}  ".format("%0.2f" % left_dist, "%0.2f" % front_dist, "%0.2f" % right_dist), 15)
        write(screen, "Loop Number: " + str(loopNum), "first", align='right')

        char = screen.getch()

        loopNum += 1

    end(screen)


if __name__ == '__main__':

    sync_esc()
    curses.wrapper(main)
