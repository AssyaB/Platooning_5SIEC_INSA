#!/usr/bin/env python3
'''Records measurments to a given file. Usage example:
$ ./record_measurments.py out1.txt'''
import sys
import can
import sys
import os
import time
HOST = ''                 # Symbolic name meaning all available interfaces
PORT = 6666              # Arbitrary non-privileged port

MCM = 0x010
MS = 0x100
US1 = 0x000
US2 = 0x001
OM1 = 0x101
OM2 = 0x102

PORT_NAME = '/dev/ttyUSB0'


if __name__ == '__main__':

    print('Bring up CAN0....')
    os.system("sudo ifconfig can0 down")
    time.sleep(0.1)
    os.system("sudo /sbin/ip link set can0 up type can bitrate 400000")
    time.sleep(0.1)

    try:
        bus = can.interface.Bus(channel='can0', bustype='socketcan_native')
    except OSError:
        print('Cannot find PiCAN board.')
        exit()

    speed =0
    cmd_mv = (50 + speed) | 0x80
    print(cmd_mv)
    msg = can.Message(arbitration_id=MCM,data=[cmd_mv, cmd_mv,0,0,0,0,0,0],extended_id=False)
    bus.send(msg)
