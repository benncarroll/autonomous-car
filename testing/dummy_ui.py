#!/usr/bin/env python

# import RPi.GPIO as GPIO
import time
import curses


# Ensure safe exit
# import atexit
# atexit.register(GPIO.cleanup)

# Steering servo GPIO Setup
steering_pin = 11
# GPIO.setmode(GPIO.BOARD)
# GPIO.setup(steering_pin, GPIO.OUT, initial=False)
# steering_servo = GPIO.PWM(steering_pin, 50)
# steering_servo.start(0)

# Throttle GPIO Setup
throttle_pin = 13
# GPIO.setup(throttle_pin, GPIO.OUT, initial=False)
# throttle_servo = GPIO.PWM(throttle_pin, 50)

# Vars
steering_bar = ['←', '\\', '|', '/', '→']
steering_list = [9.0, 8.0, 7.5, 7.0, 6.0]
steering_index = 2

throttle_bar = ['R', 'N', '1', '2', '3']
throttle_list = [6.7, 7.5, 7.9, 8, 8.1]
throttle_index = 1
prev_t_index = 1


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
    input("Please turn the car off and then on again.\nAfter it's first beep, press enter. ")
    print("Syncing...")
    # throttle_servo.start(7.5)
    time.sleep(0.5)
    # throttle_servo.ChangeDutyCycle(10)
    # time.sleep(1)
    # throttle_servo.ChangeDutyCycle(7.5)
    # time.sleep(1)
    print("Sync process completed. Launching dashboard...")
    time.sleep(0.5)
    print("\n" * 2)


def servoSet():
    global prev_t_index

    # steering_servo.ChangeDutyCycle(steering_list[steering_index])

    # prev_t_index is used to make sure the special case to engage reverse is
    # not triggered every single time an update is performed.
    if throttle_index > 0:
        # throttle_servo.ChangeDutyCycle(throttle_list[throttle_index])
        pass
    elif throttle_index == 0 and prev_t_index != 0:
        # Special case for reversing, in which the 'reverse' mode
        # acts as a brake if coming straight from accelerate mode
        # and only reverse on second entry into 'reverse' mode.
        # throttle_servo.ChangeDutyCycle(throttle_list[0])
        time.sleep(0.2)
        # throttle_servo.ChangeDutyCycle(throttle_list[1])
        time.sleep(0.2)
        # throttle_servo.ChangeDutyCycle(throttle_list[0])
    return


def end(screen):
    # Stop PWM's
    # throttle_servo.stop()
    # steering_servo.stop()
    # Make sure car is turned off.
    screen.clear()
    write(screen, "Before quitting, please turn off the car.", 5)
    write(screen, "After doing so, press any key to end.", 6)
    screen.getch()


def main(screen):

    global prev_t_index
    global steering_bar, steering_list, steering_index
    global throttle_bar, throttle_list, throttle_index

    curses.curs_set(0)
    write(screen, "▁▂▃▄▅▆▇█ Ben Carroll's Automagic Car █▇▆▅▄▃▂▁", 2)
    write(screen, "Use horizontal arrow keys to adjust steering,", 4)
    write(screen, "and vertical keys to adjust throttle.", 5)
    write(screen, "Current Steering Position", 7)
    # write(screen, "Left ----- Right", 8)
    write(screen, "Current Throttle Level", 10)
    # write(screen, "Off ----- Full", 11)

    write(screen, "Designed and Programmed by Ben Carroll", "last", "right")

    char = 0

    while True:

        prev_t_index = throttle_index

        if char == curses.KEY_RIGHT:
            if steering_index < len(steering_list) - 1:
                steering_index += 1
        if char == curses.KEY_LEFT:
            if steering_index > 0:
                steering_index -= 1

        if char == curses.KEY_UP:
            if throttle_index < len(throttle_list) - 1:
                throttle_index += 1
        if char == curses.KEY_DOWN:
            if throttle_index > 0:
                throttle_index -= 1

        if char == ord('q'):
            break

        servoSet()

        temp_s_bar = steering_bar
        s_overlay_char = temp_s_bar[steering_index]
        temp_t_bar = throttle_bar
        t_overlay_char = temp_t_bar[throttle_index]

        write(screen, ' ' + ' '.join(temp_s_bar) + ' ', 8, bar=True)
        write(screen, ' ' + ' '.join(temp_t_bar) + ' ', 11, bar=True)
        write(screen, "  Raw Throttle: {} - Raw Steering: {}  ".format(throttle_list[throttle_index], steering_list[steering_index]), 14)

        char = screen.getch()
    end(screen)


if __name__ == '__main__':

    sync_esc()
    curses.wrapper(main)
