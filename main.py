import signal
from datetime import datetime
from time import sleep
from math import sin, pi

import board
import neopixel
import schedule

OFF = (0, 0, 0)
ON = (255, 255, 255)

DOT_1 = 14
DOT_2 = 15
SEGMENT_1_OFFSET = 0
SEGMENT_2_OFFSET = 7
SEGMENT_3_OFFSET = 16
SEGMENT_4_OFFSET = 23


leds = neopixel.NeoPixel(board.D18, 30, brightness=1)
leds.fill(OFF)

running = True
dotsBlink = True
last_update = None


number_matrix = {
    -1: [OFF, OFF, OFF, OFF, OFF, OFF, OFF],
    0: [OFF, ON, ON, ON, ON, ON, ON],
    1: [OFF, OFF, OFF, ON, ON, OFF, OFF],
    2: [ON, ON, ON, OFF, ON, ON, OFF],
    3: [ON, OFF, ON, ON, ON, ON, OFF],
    4: [ON, OFF, OFF, ON, ON, OFF, ON],
    5: [ON, OFF, ON, ON, OFF, ON, ON],
    6: [ON, ON, ON, ON, OFF, ON, ON],
    7: [OFF, OFF, OFF, ON, ON, ON, OFF],
    8: [ON, ON, ON, ON, ON, ON, ON],
    9: [ON, OFF, ON, ON, ON, ON, ON],
}


def calc_brightness(now):
    # graph.tk: max\left(0,\:255\cdot \left(-2sin\left(\frac{1}{24}\cdot pi\cdot \left(x-26\right)\right)-1\right)\right)
    x = now.hour + now.minute / 60
    y = max(0, 255 * (-2 * sin(1/24 * pi * (x - 26)) - 1))
    return y


def update_brightness(now):
    new_brightness = calc_brightness(now)
    leds.brightness = new_brightness / 255


def tick():
    global last_update
    new_time = datetime.now()
    toggle_dots()

    if last_update is None or new_time.minute != last_update.minute:
        update_minutes(new_time)

    if last_update is None or new_time.hour != last_update.hour:
        update_hours(new_time)

    update_brightness(new_time)
    last_update = new_time


def toggle_dots():
    global dotsBlink
    dotsBlink = not dotsBlink
    leds[DOT_1] = ON if dotsBlink else OFF
    leds[DOT_2] = ON if dotsBlink else OFF


def display_number(offset, number, zero_is_off=False):
    if zero_is_off and number == 0:
        number = -1

    for i, state in enumerate(number_matrix[number]):
        leds[i + offset] = state


def update_hours(now):
    num1 = now.hour // 10
    num2 = now.hour % 10
    display_number(SEGMENT_1_OFFSET, num1, True)
    display_number(SEGMENT_2_OFFSET, num2, False)


def update_minutes(now):
    num1 = now.minute // 10
    num2 = now.minute % 10
    display_number(SEGMENT_3_OFFSET, num1, False)
    display_number(SEGMENT_4_OFFSET, num2, False)


def stop():
    global running
    running = False
    leds.fill(OFF)
    print()


leds.fill(OFF)
for i in range(0, 30):
    leds[i] = ON
    sleep(0.1)
leds.fill(OFF)
sleep(1)
for i in range(0, 10):
    for offset in [SEGMENT_1_OFFSET, SEGMENT_2_OFFSET, SEGMENT_3_OFFSET, SEGMENT_4_OFFSET]:
        display_number(offset, i, False)
    sleep(0.2)
leds.fill(OFF)
sleep(1)

schedule.every(1).second.do(tick)


while running:
    try:
        schedule.run_pending()
        sleep(0.5)
    except KeyboardInterrupt:
        stop()

signal.signal(signal.SIGINT, stop)
signal.signal(signal.SIGTERM, stop)
