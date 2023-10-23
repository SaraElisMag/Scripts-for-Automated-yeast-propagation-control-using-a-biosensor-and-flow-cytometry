# This script is used for testing the functionality of the other scripts while not having a pump connected.
# Essentially this is a mockup to be called in place of Pump_Handling which will send phrases without starting
# anything else.
import time


def start_pump():
    print("The pump has been started (mock).")


def stop_pump():
    print("The pump has been stopped (mock).")


def schedule_pump():
    for _ in range(1):
        start_pump()
        time.sleep(1 * 60 + 17.5)
        stop_pump()
        time.sleep(2)

    start_pump()
    time.sleep(2)
    stop_pump()


def increase_pump():
    for _ in range(1):
        start_pump()
        time.sleep(1 * 60 + 3)
        stop_pump()
        time.sleep(4)

    start_pump()
    time.sleep(5)
    stop_pump()


def fast_pump():
    for _ in range(1):
        start_pump()
        time.sleep(1 * 60 + 9)
        stop_pump()
        time.sleep(5)

    start_pump()
    time.sleep(2)
    stop_pump()


def faster_pump():
    for _ in range(1):
        start_pump()
        time.sleep(1 * 60 + 28)
        time.sleep(4)

    start_pump()
    time.sleep(5)
    stop_pump()


def constant_pump():
    for _ in range(1):
        start_pump()
        time.sleep(6)
        stop_pump()
        time.sleep(6)

    start_pump()
    time.sleep(6)
    stop_pump()