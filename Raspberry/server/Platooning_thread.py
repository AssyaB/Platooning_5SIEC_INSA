# coding: utf-8
from threading import Thread
import time
import can
import os
import struct

HOST = ''# Symbolic name meaning all available interfaces
HOSTPLAT = "10.105.1.85"
PORT = 6666              # Arbitrary non-privileged port
PORTPLAT = 7777


class MyPlatooning(Thread):

    def __init__(self,conn, bus):
        Thread.__init__(self)
        self.conn = conn
        self.bus = bus

    def run(self):
        while True :

            try:
                bus = can.interface.Bus(channel='can0', bustype='socketcan_native')
            except OSError:
                print('Cannot find PiCAN board.')
                exit()

            splat = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            splat.connect(HOSTPLAT, PORTPLAT)
            
            newthread_platoon = MyReceive(conn, bus)
            newthread_platoon.start()
            newsend_platoon = MySend(conn, bus)
            newsend_platoon.start()

            newthread_platoon.join()
            newsend_platoon.join()

            print('Received', repr(data))
