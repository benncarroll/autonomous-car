#!/usr/bin/env python

import RPi.GPIO as GPIO
import time
import curses

# Ensure safe exit
import atexit
atexit.register(GPIO.cleanup)

# Steering servo GPIO Setup
steering_pin = 11
GPIO.setmode(GPIO.BOARD)
GPIO.setup(steering_pin, GPIO.OUT, initial=False)
steering_servo = GPIO.PWM(steering_pin, 50)
steering_servo.start(0)

# Throttle GPIO Setup
throttle_pin = 13
GPIO.setup(throttle_pin, GPIO.OUT, initial=False)
throttle_servo = GPIO.PWM(throttle_pin, 50)


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


# Vars
steering_bar = ['←', '\\', '|', '/', '→']
steering_list = [9.0, 8.0, 7.5, 7.0, 6.0]
steering_index = 2
prev_s_index = 2

throttle_bar = ['R', 'N', '1', '2', '3']
throttle_list = [6.5, 7.5, 8, 8, 8.1]
# throttle_list = [6.2, 7.5, 8, 8.1, 8.2]
throttle_index = 1
prev_t_index = 1

#                 front, left, right, back
ultrasonic_list = [u_sensor(29, 31), u_sensor(35, 37), u_sensor(38, 40)]
#                 close, far
avoid_distances = [0.6, 1.5]


def write(screen, string, row, align='center', bar=False):
    dims = screen.getmaxyx()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_GREEN)

    if row == "last":
        row = dims[0] - 1

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
    if input("Please turn the car off and then on again.\nAfter it's first beep, press enter. ") != "skip":
        print("Syncing...")
        throttle_servo.start(7.5)
        time.sleep(0.5)
        throttle_servo.ChangeDutyCycle(10)
        time.sleep(2)
        throttle_servo.ChangeDutyCycle(7.5)
        time.sleep(1)
    print("Sync process completed. Loading dashboard...")
    time.sleep(0.8)
    print("\n" * 2)


def servoSet():
    global prev_t_index, prev_s_index, steering_index

    # prev_?_index is used so that the pulse width does not have
    # to be reset every cycle, possibly cutting pulses short.

    if prev_s_index != steering_index:
        if throttle_index == 0 or (throttle_index > 0 and prev_t_index == 0):

            steering_index = {
                0: 4,
                1: 3,
                2: 2,
                3: 1,
                4: 0
            }.get(steering_index)

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


def main(screen):

    # global prev_t_index,
    global steering_bar, steering_list, steering_index
    global throttle_bar, throttle_list, throttle_index

    curses.curs_set(0)
    screen.timeout(200)

    write(screen, "▁▂▃▄▅▆▇█ Ben Carroll's Automagic Car █▇▆▅▄▃▂▁", 2)
    write(screen, "This script automatically controls the the car,", 4)
    write(screen, "and does not require user input.", 5)
    write(screen, "Current Steering Position", 7)
    write(screen, "Current Throttle Level", 10)

    write(screen, "Designed and Programmed by Ben Carroll", "last", "right")

    char = 0
    paused = False
    loopNum = 0

    while True:

        loopNum += 1
        if loopNum == 20:
            loopNum = 0
            write(screen, " DEBUG ", 17, bar=True)
            screen.timeout(-1)

        elif loopNum == 0:
            write(screen, "       ", 17)
            screen.timeout(200)


        # prev_t_index = throttle_index

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

            for sensor in ultrasonic_list[:1]:

                # Get reading from sensor
                dist = sensor.get_distance()

                smallest_dist = 100
                for u in ultrasonic_list:
                    d = u.get_distance()
                    if smallest_dist > d:
                        smallest_dist = d

                # Check for further distance
                if smallest_dist <= avoid_distances[1]:

                    # If only one sensor, turn right
                    if len(ultrasonic_list) == 1:
                        steering_index = 3
                    elif len(ultrasonic_list) >= 3:
                        left_dist = ultrasonic_list[1].get_distance()
                        right_dist = ultrasonic_list[2].get_distance()
                        if left_dist > right_dist:
                            steering_index = 0
                        else:
                            steering_index = 4
                    throttle_index = 3

                # Check for closer distance
                if smallest_dist <= avoid_distances[0]:

                    # If only one sensor, turn right
                    if len(ultrasonic_list) == 1:
                        steering_index = 4
                    elif len(ultrasonic_list) >= 3:
                        left_dist = ultrasonic_list[1].get_distance()
                        right_dist = ultrasonic_list[2].get_distance()
                        if left_dist > right_dist:
                            steering_index = 0
                        else:
                            steering_index = 4
                    throttle_index = 2

            # Safety
            for sensor in ultrasonic_list:
                a = sensor.get_distance()
                if a <= .2 and a != 0.06:
                    throttle_index = 0

        # throttle_index = 1
        servoSet()

        temp_s_bar = steering_bar
        s_overlay_char = temp_s_bar[steering_index]
        temp_t_bar = throttle_bar
        t_overlay_char = temp_t_bar[throttle_index]

        write(screen, ' ' + ' '.join(temp_s_bar) + ' ', 8, bar=True)
        write(screen, ' ' + ' '.join(temp_t_bar) + ' ', 11, bar=True)
        write(screen, "  Raw Throttle: {} - Raw Steering: {} - Dist: {}  ".format(
            throttle_list[throttle_index], steering_list[steering_index], ultrasonic_list[0].get_distance()), 14)

        char = screen.getch()
    end(screen)


if __name__ == '__main__':

    sync_esc()
    curses.wrapper(main)
