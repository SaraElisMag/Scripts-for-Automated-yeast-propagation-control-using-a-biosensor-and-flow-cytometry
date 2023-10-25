import serial
import time

port = "COM7"
baudrate = 115200
ser = serial.Serial(port, baudrate)
ser.setDTR(True)


# print(ser.name)  # Unhide this and run this script if you want to find out the name of the USB port.

# This is used to control a specific pump from a specific arduino. If another pump is to be used, the user has to find
# all its specifications and replace port, baudrate and start/stop commands with the appropriate ones. it may also be
# necessary to encode/decode from a specific language (i.e. ASCII). The user also has to change the "if response =="
# to the appropriate response fraze that is sent from the pump/arduino. print(response) should let you know what the
# pump sends back, if you get b'x\00' the response is empty and something is wrong with the communication. Call the
# functions in an otherwise empty script to check functionality.

def start_pump():
    command = "G0 S1\n"
    ser.write(command.encode())
    response = ser.readline()
    # print(response)
    if response == b'>\r\n':
        print("\nThe pump has been started.")
    else:
        print("\nThere was an issue with pump communication (Incorrect response)")


def stop_pump():
    command = "G0 S0\n"
    ser.write(command.encode())
    response = ser.readline()
    # print(response)
    if response == b'>\r\n':
        print("\nThe pump has been stopped.")
    else:
        print("\nThere was an issue with pump communication (Incorrect response)")


# Calibrated for pumping rpm 043, with 1 ml/h entering the shakeflask.
def schedule_pump():
    for _ in range(1):
        start_pump()
        time.sleep(58)
        stop_pump()
        time.sleep(14 * 60)

    start_pump()
    time.sleep(58)
    stop_pump()


# Calibrated for pumping rpm 043, with 1.5 ml/h entering the shakeflask
def increase_pump():
    for _ in range(1):
        start_pump()
        time.sleep(1 * 60 + 27)
        stop_pump()
        time.sleep(13 * 60)

    start_pump()
    time.sleep(1 * 60 + 27)
    stop_pump()


# Calibrated for pumping rpm 043, with 3 ml/h entering the shakeflask
def fast_pump():
    for _ in range(1):
        start_pump()
        time.sleep(2 * 60 + 53)
        stop_pump()
        time.sleep(12)

    start_pump()
    time.sleep(2 * 60 + 53)
    stop_pump()


# Calibrated for pumping rpm 043, with 5 ml/h entering the shakeflask
def faster_pump():
    for _ in range(1):
        start_pump()
        time.sleep(4 * 60 + 49)
        stop_pump()
        time.sleep(10 * 60)

    start_pump()
    time.sleep(4 * 60 + 49)
    stop_pump()


# Calibrated for pumping rpm 043, with 10 ml/h entering the shakeflask
def constant_pump():
    for _ in range(1):
        start_pump()
        time.sleep(9 * 60 + 38)
        stop_pump()
        time.sleep(5 * 60)

    start_pump()
    time.sleep(9 * 60 + 38)
    stop_pump()