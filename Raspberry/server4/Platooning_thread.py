# coding: utf-8
from threading import *
import time
import can
import os
import struct

# Echo server program
import socket

PORTPLAT = 7777

#importing variables linked
import VarNairobi as VN

class MyReceivePlat(Thread):

    def __init__(self, splat, bus):
        Thread.__init__(self)
        self.bus = bus
        self.sock = splat
        print(self.getName(), 'initialized')

    def run(self):
        while True :
            data = self.sock.recv(1024)

            if not data: break

            data = data[2:len(data)-1]

            if VN.PlatooningActive.isSet():
                print('Received', repr(data))

        self.sock.close()


class MyPlatooning(Thread):

    def __init__(self,bus):
        Thread.__init__(self)
        self.bus = bus
        print(self.getName(), 'initialized')

    def run(self):
        while True :
            if VN.PlatooningActive.isSet():
                print(self.getName(), 'received order to start')
                splat = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                print(self.getName(), '1')
                try:
                    print(self.getName(), '2')
                    splat.connect((VN.IPPLAT, PORTPLAT))
                    print(self.getName(), '3')
                    print('Connected to', splat)
                    print(self.getName(), '4')

                    #starting Communications Thread
                    newthread_platoon = MyReceivePlat(splat, self.bus)
                    print(self.getName(), '5')
                    newthread_platoon.setName('Th-ComPlatoon')
                    print(self.getName(), '6')
                    newthread_platoon.start()
                    print(self.getName(), '7')

                    newthread_platoon.join()
                except socket.error:
                    print("Connexion error")
